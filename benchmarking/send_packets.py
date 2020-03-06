import logging

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
    iphdr.nh = 43  # Routing Header

    udphdr = UDP()
    udphdr.sport = 11111
    udphdr.dport = 3000

    payload = "$"

    return eth / iphdr / rthdr / udphdr / payload


def makeRH0(dstip, addrs):
    rh0 = IPv6ExtHdrRouting()
    rh0.type = 0
    rh0.segleft = 1
    rh0.addresses = addrs
    rh0.len = len(addrs) * 16  # Payload length in 8-bit units (128/8 = 16)

    # Receiver doesn't process this, but I feel like we should at least be getting an
    # ICMP Parameter Problem message, as per tools.ietf.org/html/rfc5095#section-3
    return makePacket(dstip, rh0)


def makeCRH16(dstip, sids):
    fmt = "BBBB" + "H" * len(sids)
    nextHeader = 17  # UDP
    extLen = len(sids) * 2  # Payload length in 8-bit units (16/8 = 2)
    routingType = 5
    segLeft = 1
    crh = pack(fmt, nextHeader, extLen, routingType, segLeft, *sids)

    return makePacket(dstip, crh)


def makeCRH32(dstip, sids):
    fmt = "BBBB" + "I" * len(sids)
    nextHeader = 17  # UDP
    extLen = len(sids) * 4  # Payload length in 8-bit units (128/32 = 4)
    routingType = 6
    segLeft = 1
    crh = pack(fmt, nextHeader, extLen, routingType, segLeft, *sids)

    return makePacket(dstip, crh)


def runSender(hdrType, size, count, numProcs, interval, verbose):
    conf.route6.flush()
    conf.route6.add(dst=C.senderRecvIp, gw=C.routerVmIp, dev=C.senderSendIf)

    if hdrType == "rh0":
        # We want to go through the router first, then
        # to our receiver, and then we don't care.
        addrs = [
            C.routerVmIp,
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
        pkt = makeRH0(C.senderRecvIp, addrs[:size])
    else:
        # Random SIDs. TODO: These will need to be set up correctly.
        sids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        if hdrType == "crh16":
            pkt = makeCRH16(C.senderRecvIp, sids[:size])
        else:
            pkt = makeCRH32(C.senderRecvIp, sids[:size])

    print(
        f"Sending {count * numProcs} {hdrType} packet(s) with "
        f"{size} device(s) and an interval of {interval}."
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
