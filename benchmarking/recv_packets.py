from pcap import pcap
from argparse import ArgumentParser
from threading import Timer
from multiprocessing import Process, Value

import constants as C

# pcap's timeout_ms option doesn't seem to be working, and I can't figure out how
# to terminate Python threads, so I'm using multiprocessing as a workaround

pktsReceived = Value('i', lock=False)


def sniff(expectedCount, verbose):
    def onPktReceived():
        nonlocal verbose
        pktsReceived.value += 1
        if verbose:
            print(pktsReceived.value)

    sniffer = pcap(name="enp0s9", promisc=False, immediate=True)
    sniffer.setfilter("ip6 and not icmp6")
    sniffer.loop(expectedCount, lambda ts, pkt : onPktReceived())


def main(expectedCount, timeout, verbose):
    p = Process(target=sniff, args=(expectedCount, verbose))
    def timeout():
        nonlocal p
        p.terminate()

    Timer(args.timeout, timeout).start()
    p.start()
    p.join()


if __name__ == "__main__":
    parser = ArgumentParser("Receive RH0 and CRH packets.")
    parser.add_argument("-c", "--count", type=int, default=C.defaultCount,
        help="The number of packets expected.")
    parser.add_argument("-t", "--timeout", type=int, default=10,
        help="The number of seconds to sniff for.")
    parser.add_argument("-v", "--verbose", default=False, action="store_true",
        help="Print stuff.")
    args = parser.parse_args()

    main(args.count, args.timeout, args.verbose)
    print(f"Received {pktsReceived.value} packets.")
