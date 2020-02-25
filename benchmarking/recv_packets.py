from pcap import pcap
from argparse import ArgumentParser
from threading import Thread
from time import sleep

import constants as C

pktsReceived = 0

def sniff(count, verbose):
    pktFilter = "ip6 and not icmp6"
    sniffer = pcap(name="enp0s9", promisc=False, immediate=True)
    sniffer.setfilter(pktFilter)

    def onPktReceived():
        global pktsReceived
        nonlocal verbose
        pktsReceived += 1
        if verbose:
            print(pktsReceived)

    sniffer.loop(count, lambda ts, pkt : onPktReceived())


if __name__ == "__main__":
    parser = ArgumentParser("Receive RH0 and CRH packets.")
    parser.add_argument("-c", "--count", type=int, default=C.defaultCount,
        help="The number of packets expected.")
    parser.add_argument("-t", "--timeout", type=int, default=10,
        help="The number of seconds to sniff for.")
    parser.add_argument("-v", "--verbose", default=False, action="store_true",
        help="Print stuff.")
    args = parser.parse_args()

    pktsReceived = 0
    pktFilter = "ip6 and not icmp6"
    sniffer = pcap(name="enp0s9", promisc=False)
    sniffer.setfilter(pktFilter)

    # pcap's timeout_ms option doesn't seem to be working, so
    # we'll just put it in a thread and wait for a bit.
    Thread(target=sniff, args=(args.count, args.verbose), daemon=True).start()
    sleep(args.timeout)

    print(f"Received {pktsReceived} packets.")
