from scapy.all import sniff, Packet, ls

pktsReceived = 0

def packetFilter(pkt):
    return hasattr(pkt, "nh") and pkt.nh == 43

def onPacketReceived(pkt):
    global pktsReceived
    pktsReceived += 1
    print(pktsReceived)
    print(pkt.summary())

if __name__ == "__main__":
    sniff(lfilter=packetFilter, store=False, count=0, iface="enp0s8", prn=onPacketReceived)
