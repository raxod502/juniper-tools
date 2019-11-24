#!/usr/bin/env bash

set -e
set -o pipefail

if (( $# != 1 )); then
    echo "usage: send_lgpkt.bash <host>" >&2
    exit 1
fi

host="$1"

# Change directory to root of juniper-tools repository.
cd "$(dirname "$0")"/..

cat large_packet.txt > "/dev/udp/${host}/3000"
