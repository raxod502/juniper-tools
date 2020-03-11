SHELL=/bin/bash

# These defaults produced decent results with -p 5 -c 10 -i 0.1

# OUtgong rate limit kbit/s
RATE=100
# Max number of bytes that can be queued waiting for tokens to become available
LIMIT=200
# Max amount of bytes that tokens can be available for instantaneously 
# (probably don't need to change this)
BUF=1000

tcpdump:
	sudo tcpdump -t -n -q -K -p -# --direction=in -c 10000 -i enp0s9 -B 131072 ip6 and not icmp6

rxtx:
	@ifconfig | egrep "enp0s8" -A 7 | egrep "enp0s8|RX"
	@ifconfig | egrep "enp0s9" -A 7 | egrep "enp0s9|TX"

limit:
	sudo tc qdisc change dev enp0s9 root tbf rate $(RATE)kbit limit $(LIMIT) buffer $(BUF) \
	|| sudo tc qdisc add dev enp0s9 root tbf rate $(RATE)kbit limit $(LIMIT) buffer $(BUF)

nolimit:
	sudo tc qdisc delete dev enp0s9 root tbf rate $(RATE)kbit limit $(LIMIT) buffer $(BUF)

show:
	tc -s qdisc ls dev enp0s9