from argparse import ArgumentParser
from threading import Timer
from multiprocessing import Process, Value

import sys
import subprocess

pktsReceived = Value("i", lock=False)


# subprocess.run
def runReceiver(expectedCount, timeoutSec, bufferSize, verbose):
    pktsReceived.value = 1

    try:
        p = subprocess.run(
            (
                "sudo",
                "tcpdump",
                "-l",
                "-c",
                str(expectedCount),
                "-t",
                "-n",
                "-q",
                "-K",
                "-p",
                "-Q",
                "in",
                "-B",
                str(bufferSize),
                "-i",
                "enp0s9",
                "ip6 and not icmp6",
            ),
            # Cannot use PIPE with timeout :(
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            timeout=timeoutSec,
        )
    except subprocess.TimeoutExpired:
        pktsReceived.value = 0

    sys.stderr.flush() # Sometimes it gets stuck, idk why
