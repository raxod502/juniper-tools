from pcap import pcap
from argparse import ArgumentParser
from threading import Timer
from multiprocessing import Process, Value
import pcapy

# pcap's timeout_ms option doesn't seem to be working, and I can't figure out how
# to terminate Python threads, so I'm using multiprocessing as a workaround

pktsReceived = Value('i', lock=False)

def sniff(expectedCount, verbose):
    def onPktReceived():
        nonlocal verbose
        pktsReceived.value += 1
        if verbose:
            print(pktsReceived.value)

    sniffer = pcap(name="enp0s9", promisc=False, immediate=True)
    sniffer.setfilter("ip6 and not icmp6")
    sniffer.loop(expectedCount, lambda ts, pkt : onPktReceived())


def runReceiver(expectedCount, timeout_sec, verbose):
    p = Process(target=sniff, args=(expectedCount, verbose))
    def timeout():
        nonlocal p
        p.terminate()

    Timer(timeout_sec, timeout).start()
    p.start()
    p.join()


# if __name__ == "__main__":
#     sniffer = pcapy.create("enp0s9")
#     sniffer.set_snaplen(10)
#     sniffer.set_promisc(False)
#     sniffer.set_buffer_size(1638400000)
#     sniffer.activate()
#     sniffer.setfilter("ip6 and not icmp6")


#     # sniffer.loop(5, lambda hdr, pkt: print(pkt))
#     sniffer.dispatch(5, lambda hdr, pkt: print(pkt)) # callback not working

#     # count = 0
#     # while count < 5:
#     #     hdr, pkt = sniffer.next()
#     #     count += 1
#     #     print(count)


#     print("DONE")
#     print(sniffer.stats())
#     sniffer.close()
