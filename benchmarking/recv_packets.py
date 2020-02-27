from pcap import pcap
from argparse import ArgumentParser
from threading import Timer
from multiprocessing import Process, Value
# import pcapy
import subprocess

# pcap's timeout_ms option doesn't seem to be working, and I can't figure out how
# to terminate Python threads, so I'm using multiprocessing as a workaround

pktsReceived = Value('i', lock=False)

# def sniff(expectedCount, verbose):
#     def onPktReceived():
#         nonlocal verbose
#         pktsReceived.value += 1
#         if verbose:
#             print(pktsReceived.value)

#     sniffer = pcap(name="enp0s9", promisc=False, immediate=True)
#     sniffer.setfilter("ip6 and not icmp6")
#     sniffer.loop(expectedCount, lambda ts, pkt : onPktReceived())


def runReceiver(expectedCount, timeout_sec, verbose):
    pktsReceived.value = True

    p = subprocess.Popen(
        ('sudo', 'tcpdump', '-l', '-c', str(expectedCount), '-t', '-n', '-q', '-K', '-p',
        '-Q', 'in', '-B' , '16384', '-i', 'enp0s9', 'ip6 and not icmp6'),
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)

    def timeout():
        nonlocal p
        global pktsReceived
        p.stdout.close()
        p.terminate()
        pktsReceived.value = False
    Timer(timeout_sec, timeout).start()

    # count = 0
    # for _ in iter(p.stdout.readline, b''):
    #     count += 1
    #     if verbose:
    #         print(count)
    #     if count == 10000:
    #         p.stdout.close()
    #         p.stderr.close()
    #         break
