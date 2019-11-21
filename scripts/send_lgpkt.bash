#!/usr/bin/env bash

cat large_packet.txt > /dev/udp/$1/3000
