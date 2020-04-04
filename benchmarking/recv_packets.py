from argparse import ArgumentParser
from threading import Timer
from multiprocessing import Process, Value

import re
import sys
import subprocess

pktsReceived = Value("i", lock=False)


def runReceiver(expectedCount, timeoutSec, bufferSize, verbose):
    pktsReceived.value = 0

    p = subprocess.run(
        (
            "sudo",
            "timeout",
            str(timeoutSec),
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
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    m = re.search(r"([0-9]+) packets captured", p.stdout.decode())
    if m:
        pktsReceived.value = int(m.group(1))
