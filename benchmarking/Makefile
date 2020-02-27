SHELL=/bin/bash

tcpdump:
	sudo tcpdump -t -n -q -K -p -# --direction=in -c 10000 -i enp0s9 -B 16384 ip6 and not icmp6
