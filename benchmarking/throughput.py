#!/usr/bin/env python3

from argparse import ArgumentParser
from multiprocessing import Process
from time import sleep
from random import random
from sys import stderr
import os
import json
import sys

import bisector
from send_packets import runSender, timeToSend
from recv_packets import runReceiver, pktsReceived
import constants as C


def runTests(args):
    total = 0
    startInterval = args.interval
    for i in range(args.numTests):
        args.interval = startInterval
        throughput = runSingleTest(args, i)
        if throughput < 0:
            print("Encountered error. Ignoring this test!", file=stderr)
            continue
        print(f"  Throughput for test {i}: {throughput}")
        total += throughput

    return total / args.numTests


def runSingleTest(args, testNum):
    """
    Approximates and returns the throughput of the router using binary
    search.
    """
    print(f"\n----------------")
    print(f"- Test #{testNum}")
    print(f"----------------")
    i = 0

    def test_fn(interval):
        nonlocal i
        args.interval = interval
        result = runIteration(args, i)
        i += 1
        return result

    bisector.bisect(
        test_fn,
        starting_value=args.interval,
        starting_velocity=args.velocity,
        accuracy=args.accuracy,
    )

    return args.count * args.processes / timeToSend.value


def sendReceivePackets(args):
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
            args.routerVmEth,
        ),
    )
    # Approximately account for time to send packets
    timeout = args.timeout + args.interval * args.count
    pRecv = Process(
        target=runReceiver,
        args=(args.count * args.processes, timeout, args.buffer, args.verbose),
    )

    pRecv.start()
    # Let receiver get started.
    sleep(1)
    pSend.start()
    pSend.join()
    pRecv.join()

    return pktsReceived.value


def runIteration(args, iterNum):
    """
    Runs an iteration of sending and receiving packets.
    Returns True if all packets were received.
    """
    print(f"\nIteration #{iterNum}")

    receivedPkts = sendReceivePackets(args)
    expectedPkts = args.count * args.processes
    if receivedPkts >= expectedPkts:
        print(f"Received all {expectedPkts} packets.")
        return True
    else:
        print(
            f"Did not receive all the packets (only got {receivedPkts} out of {expectedPkts})."
        )
        return False


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


def doActualVersusAttempted(args):
    num_incrs = args.actual_versus_attempted_increments
    points = []
    base_interval = args.interval
    for j in range(num_incrs):
        args.interval = base_interval * 2 * (j / num_incrs)
        print(f"===== Interval {args.interval:.04f}s")
        for i in range(args.numTests):
            num_sent = args.count * args.processes
            num_received = sendReceivePackets(args)
            time_taken = timeToSend.value
            attempted_throughput = num_sent / time_taken
            actual_throughput = num_received / time_taken
            print(
                f"  Attempted {attempted_throughput}, actual {actual_throughput} ({num_received}/{num_sent} packets received)"
            )
            points.append((attempted_throughput, actual_throughput))
    with open(args.dataFile, "w") as f:
        json.dump(points, f)


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
        default=0.1,
        help="The starting time (in seconds) between sending two packets.",
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
        "-a",
        "--accuracy",
        type=float,
        default=0.95,
        help="How accurate to get the interval before measuring throughput.",
    )
    parser.add_argument(
        "-V",
        "--velocity",
        type=float,
        default=1.5,
        help="Starting velocity for the binary search (see bisector docstring).",
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
        "-/",
        "--actual-versus-attempted",
        default=False,
        action="store_true",
        help="Collect data for a graph of actual versus attempted throughput.",
    )
    parser.add_argument(
        "-x",
        "--actual-versus-attempted-increments",
        type=int,
        default=20,
        help="Number of x-values for actual versus attempted throughput.",
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
        args.routerVmEth = "08:00:27:e4:a8:2e"
    elif args.machine == "crh":
        args.routerVmIp = "fde4:8dba:82e0::c5"
        args.routerVmEth = "08:00:27:e4:a8:2f"
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

    if args.actual_versus_attempted:
        doActualVersusAttempted(args)
        exit(0)

    if args.sendOnly:
        runSender(
            args.type,
            args.size,
            args.count,
            args.processes,
            args.interval,
            args.verbose,
            args.routerVmIp,
            args.routerVmEth,
        )
        exit(0)

    throughput = runTests(args)
    print(f"\nAvg Throughput: {throughput} packets/second")

    writeJson(args.dataFile, args.type, args.size, throughput)
