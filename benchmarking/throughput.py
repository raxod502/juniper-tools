#!/usr/bin/env python3

from argparse import ArgumentParser
from multiprocessing import Process
from time import sleep
from random import random
from sys import stderr
import os
import json
import sys

from send_packets import runSender, timeToSend
from recv_packets import runReceiver, pktsReceived
import constants as C


# TODO: REMOVE THIS WHEN WE FIGURE OUT HOW TO DROP PACKETS
def shouldDrop():
    """Artificially drop packets."""
    return random() < 0


def runTests(args):
    total = 0
    startInterval = args.interval
    for i in range(args.numTests):
        throughput = runSingleTest(args, i)
        # Reset the starting interval since we decreased it
        args.interval = startInterval
        if throughput < 0:
            # TODO: For the real thing, we should just stop altogether
            print("Encountered error. Ignoring this test!", file=stderr)
            continue
        total += throughput

    return total / args.numTests


def runSingleTest(args, testNum):
    """
    Runs iterations of sending and receiving packets until the router starts dropping.
    Returns the throughput.
    """
    print(f"\n----------------")
    print(f"- Test #{testNum}")
    print(f"----------------")
    i = 0
    prevTimeToSend = 0
    while runIteration(args, i):
        # Save last successful time to send
        prevTimeToSend = timeToSend.value
        # Decrease sending interval
        args.interval = args.interval - args.intervalDecrease
        if args.interval < 0:
            print(
                "Receiver did not drop any packets. Need to send them faster.",
                file=stderr,
            )
            return -1
        i += 1

    if prevTimeToSend == 0:
        print(
            "Receiver dropped on the first iteration. Decrease the starting interval.",
            file=stderr,
        )
        return -2

    return args.count * args.processes / prevTimeToSend


def runIteration(args, iterNum):
    """
    Runs an iteration of sending and receiving packets.
    Returns True if all packets were received.
    """
    print(f"\nIteration #{iterNum}")

    pSend = Process(
        target=runSender,
        args=(
            args.type,
            args.size,
            args.count,
            args.processes,
            args.interval,
            args.verbose,
            args.routerVmIp,
        ),
    )
    pRecv = Process(
        target=runReceiver,
        args=(args.count * args.processes, args.timeout, args.buffer, args.verbose),
    )

    pRecv.start()
    # Let receiver get started. TODO: Make this better later.
    sleep(1)
    pSend.start()
    pSend.join()
    pRecv.join()

    if shouldDrop():
        print("Artificially dropped packets.")
        return False
    elif pktsReceived.value:
        print("Received all packets.")
        return True
    else:
        print("Did not receive all the packets.")
        return False
    print(f"Took {timeToSend.value} seconds (wall clock).")


def writeJson(filename, hdrType, numDevices, throughput):
    if os.path.exists(filename):
        with open(filename) as inFile:
            data = json.load(inFile)
    else:
        data = []

    testResults = {"type": hdrType, "numEntries": numDevices, "throughput": throughput}
    data.append(testResults)

    with open(filename, "w") as outFile:
        json.dump(data, outFile)


if __name__ == "__main__":
    parser = ArgumentParser(description="Send RH0 and CRH packets.")
    parser.add_argument(
        "type",
        choices=["reg", "srh", "rh0", "crh16", "crh32"],
        help="Type of routing extension header",
    )
    parser.add_argument(
        "-m", "--machine", choices=["rh0", "crh"], help="Which VM to send to"
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        default=5,
        help="The number of IP addresses in the routing extension header",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=5,
        help="The number of packets to send PER SENDER PROCESS.",
    )
    parser.add_argument(
        "-p",
        "--processes",
        type=int,
        default=10,
        help="The number of sender processes.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=0,
        help="The time (in seconds) between sending two packets.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="The number of seconds to sniff for.",
    )
    parser.add_argument(
        "-b",
        "--buffer",
        type=int,
        default=131072,
        help="The tcpdump buffer size, in KiB.",
    )
    parser.add_argument(
        "-n",
        "--numTests",
        type=int,
        default=5,
        help="The total number of trials to run.",
    )
    parser.add_argument(
        "-d",
        "--intervalDecrease",
        type=float,
        default=0.01,
        help="The amount to decrease the interval after each iteration.",
    )
    parser.add_argument(
        "-f",
        "--dataFile",
        type=str,
        default="data.json",
        help="The JSON file to write test results to.",
    )
    parser.add_argument(
        "-S",
        "--sendOnly",
        default=False,
        action="store_true",
        help="Only send packets.",
    )
    parser.add_argument(
        "-v", "--verbose", default=False, action="store_true", help="Print stuff."
    )
    args = parser.parse_args()

    if not args.machine:
        if args.type == "rh0":
            args.machine = "rh0"
        else:
            args.machine = "crh"

    if args.machine == "rh0":
        args.routerVmIp = "fde4:8dba:82e0::c6"
    elif args.machine == "crh":
        args.routerVmIp = "fde4:8dba:82e0::c5"
    else:
        assert False, f"bad machine: {args.machine}"

    if args.processes > 100:
        response = input(
            f"You are about to start {args.processes} processes. Continue? (y|n).\n"
        )
        while True:
            if response == "y":
                break
            if response == "n":
                exit(0)
            response = input('Enter "y" or "n"\n')

    # Automatically re-run with sudo if needed.
    if os.geteuid() != 0:
        os.execlp("sudo", "throughput.py", os.path.realpath(__file__), *sys.argv[1:])

    # TODO: Remove this after. Just for you Hakan!
    if args.sendOnly:
        runSender(
            args.type,
            args.size,
            args.count,
            args.processes,
            args.interval,
            args.verbose,
        )
        exit(0)

    throughput = runTests(args)
    print(f"\nAvg Throughput: {throughput} packets/second")

    writeJson(args.dataFile, args.type, args.size, throughput)
