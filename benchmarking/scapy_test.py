from scapy.all import IPv6, IPv6ExtHdrRouting, UDP, Raw, send
from struct import pack

import argparse


def makePacket(dstip, rthdr):
    iphdr = IPv6()
    iphdr.dst = dstip
    iphdr.nh = 43       # Routing Header

    udphdr = UDP()
    udphdr.sport = 11111
    udphdr.dport = 3000
    
    payload = "$"

    return iphdr / rthdr / udphdr / payload


def makeRH0(dstip, addrs):
    rh0 = IPv6ExtHdrRouting()
    rh0.type = 0
    rh0.segleft = 1
    rh0.addresses = addrs
    rh0.len = len(addrs) * 16 # Payload length in 8-bit units (128/8 = 16)

    # Receiver doesn't process this, but I feel like we should at least be getting an
    # ICMP Parameter Problem message, as per tools.ietf.org/html/rfc5095#section-3
    return makePacket(dstip, rh0)


def makeCRH16(dstip, sids):
    fmt = "BBBB" + "H" * len(sids)
    nextHeader = 17        # UDP
    extLen = len(sids) * 2 # Payload length in 8-bit units (16/8 = 2)
    routingType = 5
    segLeft = 1
    crh = pack(fmt, nextHeader, extLen, routingType, segLeft, *sids)
    
    return makePacket(dstip, crh)


def makeCRH32(dstip, sids):
    fmt = "BBBB" + "I" * len(sids)
    nextHeader = 17        # UDP
    extLen = len(sids) * 4 # Payload length in 8-bit units (128/32 = 4)
    routingType = 6
    segLeft = 1
    crh = pack(fmt, nextHeader, extLen, routingType, segLeft, *sids)
    
    return makePacket(dstip, crh)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Send RH0 and CRH packets.")
    parser.add_argument("type", choices=["rh0", "crh16", "crh32"])
    parser.add_argument("-d", "--dstip", type=str, default="2001:4860:4860::8888",  help="Destination IPv6 address")
    parser.add_argument("-n", "--numDevices", type=int, default="5", help="The number of IP addresses in the routing extension header")
    parser.add_argument("-t", "--numTimes", type=int, default="1", help="The number of times to send the packet.")
    args = parser.parse_args()

    if args.type == "rh0":
        # Random addresses
        addrs = [
            "f223:7036:7677:67e5:cca2:abe1:eec3:5718",
            "72d8:7613:5172:860f:6d70:5260:ba7b:2053",
            "b03b:c9d2:bd5d:923e:5adf:9675:e903:27ea",
            "5d45:828f:f53b:e43c:ef68:6991:a9ae:5a9b",
            "6374:f8d4:e316:fc7c:279b:5884:fd9e:ddf4",
            "5284:b7c6:4928:8a51:47bf:3e0d:9cbd:2a50",
            "e290:1cbc:2b0a:c51c:38d8:f510:70b3:fd3f",
            "ed63:2a78:7311:1d4d:f759:c6e9:cf84:e586",
            "c1ec:8eef:74bf:c76e:1482:ba94:fbea:3090",
            "d2eb:66a0:8af:9f19:21a0:cc0d:ffbe:6ad5",
            "c85d:1618:799:8c6:41c2:2dc6:83e9:175",
            "4bd7:4270:d60e:a973:5c92:b4ec:fbb3:9562"
        ]
        pkt = makeRH0(args.dstip, addrs[:args.numDevices])
    
    else:
        # Random SIDs
        sids = [1,2,3,4,5,6,7,8,9,10,11,12]
        if args.type == "crh16":
            pkt = makeCRH16(args.dstip, sids[:args.numDevices])
        else:
            pkt = makeCRH32(args.dstip, sids[:args.numDevices])

    
    for i in range(args.numTimes):
        send(pkt)