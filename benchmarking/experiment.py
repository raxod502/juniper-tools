#!/usr/bin/env python3

import subprocess

startIntervals = {"rh0": 1.0, "srh": 1.1, "crh16": 0.2}

for hdr, startI in startIntervals.items():
    for size in range(15, 0, -1):
        subprocess.run(
            (
                "sudo",
                "python3",
                "throughput.py",
                hdr,
                "-p",
                "10",
                "-c",
                "10",
                "-i",
                str(startI),
                "-n",
                "5",
                "-s",
                str(size),
                "-f",
                hdr + ".json",
                "-v",
            )
        )
        # Hack for better approximation of expected results.
        if hdr == "rh0":
            startI -= 0.05


# Regular packets with rh0 machine
subprocess.run(
    (
        "sudo",
        "python3",
        "throughput.py",
        "reg",
        "-m",
        "rh0",
        "-p",
        "10",
        "-c",
        "10",
        "-i",
        "0.1",
        "-n",
        "5",
        "-f",
        "reg_rh0.json",
        "-v",
    )
)

# Regular packets with crh machine
subprocess.run(
    (
        "sudo",
        "python3",
        "throughput.py",
        "reg",
        "-m",
        "crh",
        "-p",
        "10",
        "-c",
        "10",
        "-i",
        "0.1",
        "-n",
        "5",
        "-f",
        "reg_crh.json",
        "-v",
    )
)
