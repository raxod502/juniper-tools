from argparse import ArgumentParser
from threading import Timer
from multiprocessing import Process, Value
from subprocess import Popen, DEVNULL


pktsReceived = Value('i', lock=False)


# subprocess.run
def runReceiver(expectedCount, timeoutSec, bufferSize, verbose):
    pktsReceived.value = 1

    fd = None if verbose else DEVNULL

    p = Popen(
        ('sudo', 'tcpdump', '-l', '-c', str(expectedCount), '-#', '-t', '-n', '-q', '-K', '-p',
        '-Q', 'in', '-B' , str(bufferSize), '-i', 'enp0s9', 'ip6 and not icmp6'),
        stderr=fd,
        stdout=DEVNULL)

    def timeout():
        nonlocal p
        global pktsReceived
        print("TIMEOUT!")
        p.terminate()
        pktsReceived.value = 0

    Timer(timeoutSec, timeout).start()
    p.wait()
