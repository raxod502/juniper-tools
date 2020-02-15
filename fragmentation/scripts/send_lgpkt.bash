#!/usr/bin/env bash

set -e
set -o pipefail

if (( $# != 2 )); then
    echo "usage: send_lgpkt.bash <host> <protocol>" >&2
    exit 1
fi

host="$1"
protocol="$2"

# Change directory to root of juniper-tools repository.
cd "$(dirname "$0")"/..

cat large_packet.txt > "/dev/${protocol}/${host}/3000"
