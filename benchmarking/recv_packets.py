from scapy.all import sniff, Packet, ls, send
from argparse import ArgumentParser

pktsReceived = 0

def packetFilter(pkt):
    return hasattr(pkt, "nh") and pkt.nh == 43


def onPacketReceived(pkt):
    global pktsReceived
    pktsReceived += 1
    print(pktsReceived)
    print(pkt.summary())


if __name__ == "__main__":
    parser = ArgumentParser("Receive RH0 and CRH packets.")
    parser.add_argument("-c", "--count", type=int, default=5,
        help="The number of packets expected.")
    parser.add_argument("-t", "--timeout", type=int, default=5,
        help="The number of seconds to sniff for.")
    args = parser.parse_args()

    expectedCount = args.count

    sniff(
        lfilter=packetFilter,
        store=False,
        timeout=args.timeout,
        count=args.count,
        iface="enp0s9",
        prn=onPacketReceived)
