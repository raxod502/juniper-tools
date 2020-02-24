#!/bin/sh

if [ "$1" -gt "100" ]; then
    echo "You are about to start $1 processes. Press y to continue, any other key to exit."
    read answer
    if [ "$answer" != "y" ]; then
        exit 0
    fi
fi

for i in $(seq "$1"); do
    sudo python3 send_packets.py rh0 -c "$2" &
done
