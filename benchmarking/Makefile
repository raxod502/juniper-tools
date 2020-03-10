SHELL=/bin/bash

# Delay per packet
DELAY=4
# Loss %
LOSS=20
# Rate limit bit/s
RATE=1
# Max size of TX queue
LIMIT=10

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
	sudo tc qdisc delete dev enp0s9 root netem loss $(LOSS)%

rate:
	sudo tc qdisc change dev enp0s9 root netem rate $(RATE)bit \
	|| sudo tc qdisc add dev enp0s9 root netem rate $(RATE)bit

norate:
	sudo tc qdisc delete dev enp0s9 root netem rate $(RATE)bit

limit:
	sudo tc qdisc change dev enp0s9 root netem limit $(LIMIT) \
	|| sudo tc qdisc add dev enp0s9 root netem limit $(LIMIT)

nolimit:
	sudo tc qdisc delete dev enp0s9 root netem limit $(LIMIT)
