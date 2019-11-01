#!/usr/bin/env bash

cat ~/juniper-tools/large_packet.txt > /dev/udp/$1/3000
