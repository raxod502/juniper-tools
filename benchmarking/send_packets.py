import logging
import ipaddress

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import Ether, IPv6, IPv6ExtHdrRouting, UDP, sendp, ls, conf
from struct import pack
from time import time
from argparse import ArgumentParser
from multiprocessing import Process, Value

import constants as C


timeToSend = Value("d", lock=False)


def makePacket(dstip, rthdr):
    # MAC address of router interface on senderSend private network.
    # Don't know why Scapy can't figure this out on its own.
    eth = Ether(dst="08:00:27:e4:a8:2f")

    iphdr = IPv6()
    iphdr.dst = dstip
    # this is necessary for srh
    iphdr.src = C.senderSendIp
    # Routing Header = 43, UDP = 17
    iphdr.nh = 17 if rthdr == "" else 43

    udphdr = UDP()
    udphdr.sport = 11111
    udphdr.dport = 3000

    payload = "$"

    return eth / iphdr / rthdr / udphdr / payload


def makeRegular(dstip):
    return makePacket(dstip, "")


def makeRH0(dstip, addrs):
    rh0 = IPv6ExtHdrRouting()
    rh0.type = 0
    rh0.segleft = len(addrs)
    rh0.addresses = addrs
    rh0.len = len(addrs) * 2  # Payload length in 8-byte units (128/8 = 16)

    return makePacket(dstip, rh0)


def makeCRH16(dstip, sids):
    fmt = "!BBBB" + "H" * len(sids)
    nextHeader = 17  # UDP
    byteLen = 4 + len(sids) * 2  # length of header in bytes before padding
    extLen = (byteLen - 1) // 8  # length of header in 8 byte units

    bytesToFill = 8 * (extLen + 1) - byteLen  # need to pad the rest
    fmt += "B" * bytesToFill
    for i in range(bytesToFill):
        sids.append(0)

    routingType = 5
    segLeft = 1
    crh = pack(fmt, nextHeader, extLen, routingType, segLeft, *sids)

    return makePacket(dstip, crh)


def makeCRH32(dstip, sids):
    fmt = "!BBBB" + "I" * len(sids)
    nextHeader = 17  # UDP
    byteLen = 4 + len(sids) * 4  # length of header in bytes before padding
    extLen = (byteLen - 1) // 8  # length of header in 8 byte units

    bytesToFill = 8 * (extLen + 1) - byteLen  # need to pad the rest
    fmt += "B" * bytesToFill
    for i in range(bytesToFill):
        sids.append(0)

    routingType = 6
    segLeft = 1
    crh = pack(fmt, nextHeader, extLen, routingType, segLeft, *sids)

    return makePacket(dstip, crh)


def makeSRH(dstip, addrs):
    fmt = "BBBB" + "BBH" + str((len(addrs) + 2) * 16) + "s"

    nextHeader = 17  # UDP
    extLen = (len(addrs) + 2) * 2  # length of header in bytes
    routingType = 4
    segLeft = len(addrs) + 1
    firstSeg = len(addrs) + 1
    flags = 0
    reserved = 0

    segs = bytearray()
    for i in range(len(addrs)):
        addr = ipaddress.IPv6Address(addrs[i])
        segs.extend(addr.packed)

    destIp = ipaddress.IPv6Address(C.senderRecvIp)
    srcIp = ipaddress.IPv6Address(dstip)
    segs.extend(destIp.packed)
    segs.extend(srcIp.packed)

    srh = pack(
        fmt, nextHeader, extLen, routingType, segLeft, firstSeg, flags, reserved, segs,
    )

    return makePacket(dstip, srh)


def runSender(hdrType, size, count, numProcs, interval, verbose, routerVmIp):
    conf.route6.flush()
    conf.route6.add(dst=C.senderRecvIp, gw=routerVmIp, dev=C.senderSendIf)

    if hdrType == "rh0":
        # We want to go through the router first, then
        # to our receiver, and then we don't care.
        addrs = [
            C.senderRecvIp,
            "b03b:c9d2:bd5d:923e:5adf:9675:e903:27ea",
            "5d45:828f:f53b:e43c:ef68:6991:a9ae:5a9b",
            "6374:f8d4:e316:fc7c:279b:5884:fd9e:ddf4",
            "5284:b7c6:4928:8a51:47bf:3e0d:9cbd:2a50",
            "e290:1cbc:2b0a:c51c:38d8:f510:70b3:fd3f",
            "ed63:2a78:7311:1d4d:f759:c6e9:cf84:e586",
            "c1ec:8eef:74bf:c76e:1482:ba94:fbea:3090",
            "d2eb:66a0:8af:9f19:21a0:cc0d:ffbe:6ad5",
            "c85d:1618:799:8c6:41c2:2dc6:83e9:175",
            "4bd7:4270:d60e:a973:5c92:b4ec:fbb3:9562",
        ]
        pkt = makeRH0(routerVmIp, addrs[:size])
    elif hdrType == "reg":
        pkt = makeRegular(C.senderRecvIp)
    elif hdrType == "srh":
        addrs = [
            # we add the sender destination address later
            "b03b:c9d2:bd5d:923e:5adf:9675:e903:27ea",
            "5d45:828f:f53b:e43c:ef68:6991:a9ae:5a9b",
            "6374:f8d4:e316:fc7c:279b:5884:fd9e:ddf4",
            "5284:b7c6:4928:8a51:47bf:3e0d:9cbd:2a50",
            "e290:1cbc:2b0a:c51c:38d8:f510:70b3:fd3f",
            "ed63:2a78:7311:1d4d:f759:c6e9:cf84:e586",
            "c1ec:8eef:74bf:c76e:1482:ba94:fbea:3090",
            "d2eb:66a0:8af:9f19:21a0:cc0d:ffbe:6ad5",
            "c85d:1618:799:8c6:41c2:2dc6:83e9:175",
            "4bd7:4270:d60e:a973:5c92:b4ec:fbb3:9562",
        ]
        pkt = makeSRH(routerVmIp, addrs[: (size - 2)])
    else:
        # Random SIDs. TODO: These will need to be set up correctly.
        sids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        if hdrType == "crh16":
            pkt = makeCRH16(routerVmIp, sids[:size])
        else:
            pkt = makeCRH32(routerVmIp, sids[:size])

    print(
        f"Sending {count * numProcs} {hdrType} packet(s) with "
        f"{size} device(s) and an interval of {interval:.3f}."
    )

    pSenders = [
        Process(
            target=sendp,
            args=(pkt),
            kwargs={
                "count": count,
                "inter": interval,
                "iface": C.senderSendIf,
                "verbose": 0,
            },
        )
        for _ in range(numProcs)
    ]

    # This timing will be awful, but Ron has an IXIA so I'm not really worried about it.
    start = time()
    for p in pSenders:
        p.start()
    for p in pSenders:
        p.join()
    stop = time()

    timeToSend.value = stop - start
    if verbose:
        print(f"Time to send all packets: {timeToSend.value}")
