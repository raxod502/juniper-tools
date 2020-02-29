SHELL=/bin/bash

tcpdump:
	sudo tcpdump -t -n -q -K -p -# --direction=in -c 10000 -i enp0s9 -B 16384 ip6 and not icmp6

showRxTx:
	@ifconfig | egrep "enp0s8" -A 7 | egrep "enp0s8|RX"
	@ifconfig | egrep "enp0s9" -A 7 | egrep "enp0s9|TX"
