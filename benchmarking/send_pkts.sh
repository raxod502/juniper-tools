#!/bin/sh

for i in $(seq "$1")
do
    sudo python3 send_packets.py rh0 -c "$2" &
done
