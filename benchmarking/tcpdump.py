import pcapy
import subprocess as sub
from time import sleep

if __name__ == "__main__":
    # sniffer = pcapy.create("enp0s9")
    # sniffer.set_snaplen(10)
    # sniffer.set_promisc(False)
    # sniffer.set_buffer_size(1638400000)
    # sniffer.activate()
    # sniffer.setfilter("ip6 and not icmp6")


    # # sniffer.loop(5, lambda hdr, pkt: print(pkt))
    # sniffer.dispatch(5, lambda hdr, pkt: print(pkt)) # callback not working

    # # count = 0
    # # while count < 5:
    # #     hdr, pkt = sniffer.next()
    # #     count += 1
    # #     print(count)


    # print("DONE")
    # print(sniffer.stats())
    # sniffer.close()

# sudo tcpdump -t -n -q -K -p -# --direction=in -c 10000 -i enp0s9 -B 16384 ip6 and not icmp6
    # tcpdump = subprocess.Popen(["sudo", "tcpdump", "-l", "-c 1", "i enp0s9", "-B 16384", "ip6 and not icmp6"], stdout=subprocess.PIPE)

    # tcpdump = subprocess.Popen("sudo tcpdump -t -n -q -K -p -# --direction=in -c 10000 -i enp0s9 -B 16384 ip6 and not icmp6", shell=True, stdout=subprocess.PIPE)
    # for row in iter(tcpdump.stdout.readline, b''):
    #     print(row.rstrip())
    #     print("hi")

    count = 0
    p = sub.Popen(('sudo', 'tcpdump', '-l', '-t', '-n', '-q', '-K', '-p', '-Q', 'in', '-B' , '16384', '-i', 'enp0s9', 'ip6 and not icmp6'), stdout=sub.PIPE)
    for _ in iter(p.stdout.readline, b''):
        count += 1
        print(count)
        if count == 10000:
            break

    p.terminate()


    # output = subprocess.check_output(["grep", "packets received by filter"], stdin=proc1.stdout)
    # proc1.wait()
    # print(output)

    # p = sub.Popen(('sudo', 'tcpdump', '-l'), stdout=sub.PIPE)
