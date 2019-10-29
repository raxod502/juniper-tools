#!/usr/bin/env bash

set -e
set -o pipefail

if (( $# == 0 )); then
    echo "usage: update-config.bash <linux-srcdir>" >&2
    exit 1
fi

srcdir="$1"

rm -f "${srcdir}/.config"
make -C "${srcdir}" tinyconfig

cat .config | grep -vE "^(#|$)" | while read line; do
    key="$(echo "$line" | grep -m1 -o "^[^=]*" | head -n1)"
    echo "juniper-tools: setting $line" >&2
    echo "key |$key|"
    # Really slow but works for now.
    sed -E -i "s~.*(^| )${key}[= ].*~${line}~" "${srcdir}/.config"
done
