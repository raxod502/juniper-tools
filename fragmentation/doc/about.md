([back to README](../README.md))

This document explains the problem that our Clinic project solves, and
the approach that we took.

## Background on IP fragmentation

Our project deals with the Internet Protocol version 4 (IPv4). The
objective of IPv4 is to route packets from a source to a destination
through a sequence of intermediate routers. However, every link
between two routers has an associated limit on the size of packets
that it can handle, called the Maximum Transmission Unit (MTU).
Unfortunately, MTUs vary dramatically between links. Typical values
range from 50 to 1500 bytes.

When a packet must be sent through a link whose MTU is too small for
it, IPv4 fragments the packet into smaller pieces which can be sent
individually and then reassembled at the destination. This ensures
that packets will be delivered, but it has serious performance
implications. The main issue is that receiving fragmented packets is
significantly slower than receiving unfragmented packets, since
expensive operations must be performed to reassemble the fragments
correctly and since the destination must keep all received fragments
in memory for a relatively long time until either the final fragment
is received or until a timeout.

For this reason, it is desirable to avoid fragmentation.

The standard approach to this is called Path MTU Discovery (PMTUD).
Under PMTUD, the Don't Fragment (DF) option is set on all transmitted
packets. With DF, when a packet reaches a link whose MTU is too small,
the router will drop it and return an ICMP (Internet Control Message
Protocol) Destination Unreachable message to the source. The ICMP
message includes the MTU of the relevant link, which informs the
source that it needs to retransmit that data, but split it into
smaller packets based on the MTU. If a subsequent link on the path to
the destination has an even smaller MTU, this process may repeat
several times before a packet is successfully delivered. PMTUD allows
the source to estimate the MTU of the smallest link on the path to the
destination, which is called the path MTU (PMTU). After PMTUD,
transmitted packets have exactly the PMTU. (Note, however, that PMTUD
is not just performed at the initialization of a connection. It also
happens implicitly whenever the PMTU decreases, which might happen due
to load balancing or changes in network topology.)

PMTUD has several problems. One issue is that it is slow. Although it
avoids fragmentation, it increases latency on the delivery of some
packets because messages must be sent back and forth synchronously
before the too-large packet can be delivered successfully. With
fragmentation, on the other hand, all packets that are sent can be
delivered without a round trip, even if their processing is slower.
PMTUD trades one performance problem for a different one.

A much more serious shortcoming of PMTUD is called blackholing. This
occurs when an intermediate router fails to pass along ICMP
Destination Unreachable messages. Routers may do this for security
reasons (since emitting less diagnostic information makes an attack on
the network more difficult) or because they are misconfigured. In
either case, if the ICMP message is never delivered, then the source
will never be informed that the packet it sent was too large. Under
the Transmission Control Protocol (TCP), in which every data packet
sent triggers an acknowledgement (ACK) packet in response, the source
will notice from the absence of an ACK that its packet was not
delivered. However, it will not know to split the data into smaller
packets, so it will fall into an infinite loop sending the same packet
over and over again. This failure condition is much worse than the
degraded performance of fragmentation.

A final issue with PMTUD is that it is not compatible with all
protocols. For example, the User Datagram Protocol (UDP) does not have
the notion of a persistent connection between source and destination
(for example, it supports multicast, wherein a single packet can be
addressed to multiple destinations, each of which might have its own
distinct PMTU). For this reason, it does not make conceptual sense for
the source to generate a PMTU estimate by setting DF.

IPv6, the successor to IPv4, uses PMTUD exclusively and disallows
fragmentation except at the source node. However, fragmentation is
still allowed in IPv4, and our Clinic project implements a better
solution to the fragmentation problem which replaces PMTUD.

## Approach

We propose a new type of ICMP message, called Packet Reassembled. An
IPv4 host emits this message when it successfully reassembles a
fragmented packet, addressing the message to the source of the
fragmented packet. ICMP Packet Reassembled includes the size of the
largest fragment that was received. Note that this size is guaranteed
not to exceed the PMTU, and is likely to equal it exactly. For this
reason, the source host can inspect this message and know that it
should send smaller packets. In other words, ICMP Packet Reassembled
serves the same function for the source host as ICMP Destination
Unreachable.

However, its different usage has several key advantages. For one
thing, fragmentation is still enabled, so the blackholing issue is
ruled out. (Note that an intermediate router could still refuse to
pass ICMP Packet Reassembled messages, but this will not cause
blackholing because data packets are still being delivered
successfully, albeit at slightly degraded performance.) Furthermore,
ICMP Packet Reassembled has lower latency than PMTUD because packets
never need to be retransmitted synchronously. In essence, the PMTU is
"discovered" asynchronously, in parallel with continuous data
transmission. Furthermore, although ICMP Packet Reassembled does not
explicitly address the issue of UDP, it is much easier to see how an
implementation of UDP could reduce fragmentation by inspecting ICMP
Packet Reassembled messages than it is to see how PMTUD could be used
for UDP.

Please refer to the published Internet Draft
[here](https://tools.ietf.org/html/draft-bonica-intarea-lossless-pmtud-01).

## Implementation

Our implementation is in the context of the Linux kernel. The patch is
provided in [`juniper.patch`](../juniper.patch) and is also available
in [our fork of the Linux source
repository](https://github.com/raxod502/juniper-linux/tree/juniper).

Here is an outline of the changes that the patch includes:

* `include/uapi/linux/icmp.h`: define the format of ICMP Packet
  Reassembled and assign it code 253, which is reserved for Internet
  experiments as per [RFC 4727](https://tools.ietf.org/html/rfc4727).
* `net/ipv4/ip_fragment.c`: send ICMP Packet Reassembled when a packet
  is reassembled.
* `net/ipv4/icmp.c`: trigger the same code when receiving ICMP Packet
  Reassembled as when receiving ICMP Destination Unreachable. Handle
  ICMP Packet Reassembled that was triggered by a reassembled ICMP
  packet.
* `net/ipv4/tcp_ipv4`: handle ICMP Packet Reassembled that was
  triggered by a reassembled TCP packet.
* `net/ipv4/udp.c`: handle ICMP Packet Reassembled that was triggered
  by a reassembled UDP packet.
* `net/ipv4/raw.c`: handle ICMP Packet Reassembled that was triggered
  by reassembly across a raw socket.
