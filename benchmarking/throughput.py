from argparse import ArgumentParser
from multiprocessing import Process
from time import sleep

from send_packets import runSender, timeToSend
from recv_packets import runReceiver, pktsReceived


if __name__ == "__main__":
    parser = ArgumentParser("Send RH0 and CRH packets.")
    parser.add_argument("type", choices=["rh0", "crh16", "crh32"],
        help="Type of routing extension header")
    parser.add_argument("-s", "--size", type=int, default=5,
        help="The number of IP addresses in the routing extension header")
    parser.add_argument("-c", "--count", type=int, default=5,
        help="The number of packets to send PER SENDER PROCESS.")
    parser.add_argument("-p", "--processes", type=int, default=10,
        help="The number of sender processes.")
    parser.add_argument("-i", "--interval", type=float, default=0,
        help="The time (in seconds) between sending two packets.")
    parser.add_argument("-t", "--timeout", type=int, default=10,
        help="The number of seconds to sniff for.")
    parser.add_argument("-v", "--verbose", default=False, action="store_true",
        help="Print stuff.")
    args = parser.parse_args()

    pSend = Process(target=runSender, args=(args.type, args.size, args.count, args.processes, args.interval, args.verbose))
    pRecv = Process(target=runReceiver, args=(args.count * args.processes, args.timeout, args.verbose))

    pRecv.start()
    # Let receiver get started. This is an unfortunate hack, but I can't set a variable
    # inside the sniffer loop
    sleep(1)
    pSend.start()
    pSend.join()
    pRecv.join()

    print(f"Received {pktsReceived.value} packets.")
    print(f"Took {timeToSend.value} seconds (wall clock).")
