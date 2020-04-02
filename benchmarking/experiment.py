import subprocess

startIntervals = {
    "rh0": 1.0,
    "srh": 1.1,
    "crh16": 0.2
}

for hdr in ["rh0", "crh16", "srh"]:
    startI = startIntervals[hdr]
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
                "2",
                "-d"
                "0.01",
                "-s",
                str(size),
                "-f",
                hdr + ".json",
                "-v"
            ))
        # Empirically, the throughput seems to increase linearly for RH0, so
        # let's keep these tests from taking forever.
        if hdr == "rh0":
            startI -= 0.05
                

# Regular packets with rh0 machine
subprocess.run(
            (
                "sudo",
                "python3",
                "throughput.py",
                "reg",
                "-p",
                "10",
                "-c",
                "10",
                "-i",
                "0.1",
                "-n",
                "2",
                "-d"
                "0.01",
                "-f",
                "reg_rh0.json",
                "-v"
            ))

# Regular packets with crh machine
subprocess.run(
            (
                "sudo",
                "python3",
                "throughput.py",
                "reg",
                "-p",
                "10",
                "-c",
                "10",
                "-i",
                "0.1",
                "-n",
                "2",
                "-d"
                "0.01",
                "-f",
                "reg_crh.json",
                "-v"
            ))