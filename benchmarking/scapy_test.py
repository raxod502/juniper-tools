from scapy.all import IPv6, IPv6ExtHdrRouting, UDP, Raw, send

import sys
import argparse
from struct import pack

def sendRH0(dstip, addrs):
    iphdr = IPv6()
    iphdr.dst = dstip

    rthdr = IPv6ExtHdrRouting()
    rthdr.type = 0
    rthdr.segleft = 0
    rthdr.addresses = addrs
    rthdr.len = len(addrs) * 16 # Length of payload (addresses) in 8-bit units

    udphdr = UDP()
    udphdr.sport = 11111
    udphdr.dport = 3000
    
    payload = "bytes"
    
    # Receiver doesn't process this, presumably because RH0 is deprecated.
    send(iphdr / rthdr / udphdr / payload)


# def sendCRH32(dstip, sids):
#     fmt = "BBBB" + "I" * len(sids)
# 
#     nextHeader = 0
#     extLen = len(sids) * 4
#     routingType = 6
#     segLeft = 0
#     crh = pack(fmt, 0, extLen, routingType,  *sids)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Send RH0 and CRH packets.")
    parser.add_argument("-d", "--dstip", type=str, default="fde4:8dba:82e1::c5",  help="Destination IPv6 address") # fde4:8dba:82e1::c5 is receiver VM
    parser.add_argument("-n", "--numDevices", type=int, default="5", help="The number of IP addresses in the routing extension header")
    args = parser.parse_args()

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

    sendRH0(args.dstip, addrs[:args.numDevices])
