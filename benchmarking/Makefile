SHELL=/bin/bash

# DEFAULTS USED FOR EXPERIMENT. DO NOT CHANGE

# Outgoing rate limit kbit/s
RATE=25
# Max number of bytes that can be queued waiting for tokens to become available
LIMIT=3000
# Bucket size (number of tokens/bytes)
BUF=3000

HOSTNAME := $(shell hostname)
ifeq ($(HOSTNAME),crh)
	IF=enp0s9
else
	IF=eth2
endif

tcpdump:
	sudo tcpdump -t -n -q -K -p -# --direction=in -c 10000 -i enp0s9 -B 131072 ip6 and not icmp6

rxtx:
	@ifconfig | egrep "enp0s8" -A 7 | egrep "enp0s8|RX"
	@ifconfig | egrep "enp0s9" -A 7 | egrep "enp0s9|TX"

# https://linux.die.net/man/8/tc-tbf
limit:
	sudo tc qdisc replace dev $(IF) root tbf rate $(RATE)kbit limit $(LIMIT) buffer $(BUF)

nolimit:
	sudo tc qdisc delete dev $(IF) root tbf rate $(RATE)kbit limit $(LIMIT) buffer $(BUF)

show:
	tc -s qdisc ls dev $(IF)

.PHONY: draft
draft:
	scripts/format_rfc.py draft/raw.txt > draft/final.txt
	cat draft/final.txt | enscript --margins 76::76: -B -q -p draft/final.ps
	ps2pdf draft/final.ps draft/final.pdf
