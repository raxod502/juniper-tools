SHELL=/bin/bash

DELAY=4
LOSS=20

tcpdump:
	sudo tcpdump -t -n -q -K -p -# --direction=in -c 10000 -i enp0s9 -B 131072 ip6 and not icmp6

rxtx:
	@ifconfig | egrep "enp0s8" -A 7 | egrep "enp0s8|RX"
	@ifconfig | egrep "enp0s9" -A 7 | egrep "enp0s9|TX"

delay:
	sudo tc qdisc change dev enp0s9 root netem delay $(DELAY)s \
	|| sudo tc qdisc add dev enp0s9 root netem delay $(DELAY)s

nodelay:
	sudo tc qdisc delete dev enp0s9 root netem delay $(DELAY)s

loss:
	sudo tc qdisc change dev enp0s9 root netem loss $(LOSS)% \
	|| sudo tc qdisc add dev enp0s9 root netem loss $(LOSS)%

noloss:
	sudo tc qdisc delete dev enp0s9 root netem loss $(LOSS)% \
