from scapy.all import sniff, Packet, ls, send
from argparse import ArgumentParser
from threading import Lock

import constants as C

def packetFilter(pkt):
    return hasattr(pkt, "nh") and pkt.nh == 43

# NOTE: We can also use "ifconfig" and check the difference between
# RX packets under enp0s8 and TX packets under enp0s9 to approximately*
# see if a lot of packets were dropped.
# *random ICMPv6 packets are also being transmitted

# TODO: Figure out why this code is wrong. Results don't match
# output from ifconfig and wireshark.
def onPacketReceived(pktsReceived, lock):
    def helper(pkt):
        nonlocal lock
        nonlocal pktsReceived
        if lock.locked():
            print("locked")
        lock.acquire()
        print(pktsReceived)
        pktsReceived += 1
        lock.release()
        return pktsReceived
    return helper


if __name__ == "__main__":
    parser = ArgumentParser("Receive RH0 and CRH packets.")
    parser.add_argument("-c", "--count", type=int, default=C.defaultCount,
        help="The number of packets expected.")
    parser.add_argument("-t", "--timeout", type=int, default=10,
        help="The number of seconds to sniff for.")
    args = parser.parse_args()

    pktsReceived = 0
    lock = Lock()

    sniff(
        lfilter=packetFilter,
        store=False,
        timeout=args.timeout,
        count=args.count,
        iface="enp0s9",
        prn=onPacketReceived(pktsReceived, lock))

    print(f"Total of {pktsReceived} packets received.")
