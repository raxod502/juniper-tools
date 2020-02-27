from argparse import ArgumentParser
from threading import Timer
from multiprocessing import Process, Value
import subprocess


pktsReceived = Value('i', lock=False)

def runReceiver(expectedCount, timeoutSec, bufferSize, verbose):
    pktsReceived.value = 1

    fd = None if verbose else subprocess.DEVNULL

    p = subprocess.Popen(
        ('sudo', 'tcpdump', '-l', '-c', str(expectedCount), '-#', '-t', '-n', '-q', '-K', '-p',
        '-Q', 'in', '-B' , str(bufferSize), '-i', 'enp0s9', 'ip6 and not icmp6'),
        stderr=fd,
        stdout=fd)

    def timeout():
        nonlocal p
        global pktsReceived
        p.stdout.close()
        p.terminate()
        pktsReceived.value = 0

    Timer(timeoutSec, timeout).start()
    p.wait()
