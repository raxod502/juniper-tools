#!/usr/bin/env python3

import subprocess

for hdr in ("rh0", "srh", "crh16", "reg_rh0", "reg_crh"):
    args = ["./throughput.py", hdr, "-/", "-f", hdr + "-ava.json"]
    if hdr == "reg_rh0":
        args.extend(("-m", "rh0"))
    subprocess.run(args)
