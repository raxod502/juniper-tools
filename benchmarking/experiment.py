import subprocess

startIntervals = {
    "rh0": 1.0,
    "srh": 1.1,
    "crh16": 0.2
}

for hdr in ["rh0", "crh16", "srh"]:
    startI = startIntervals[hdr]
    for size in range(15, 0, -1):
        p = subprocess.run(
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
                
