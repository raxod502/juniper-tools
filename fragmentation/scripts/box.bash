#!/usr/bin/env bash

set -e
set -o pipefail

if (( $# > 1 )); then
    echo "usage: scripts/box.bash MSG" >&2
    exit 1
elif (( $# == 1 )); then
    # https://stackoverflow.com/a/7359879/3538165
    # https://stackoverflow.com/a/16198793/3538165
    message="$(echo -E "$1" | sed '/./,$!d' | sed '$a\' | fmt -w75)"
else
    message="$(cat)"
fi

length="$(echo -E "$message" | awk '{ print length }' | sort -n | tail -1)"

format="%-${length}s"

underscores="$(printf "$format" "" | sed "s/./_/g")"
spaces="$(printf "$format" "" | sed "s/./ /g")"

echo " _${underscores}_ "
echo "/ ${spaces} \\"
echo -E "${message}" | while read -r line; do
    printf "| ${format} |\n" "$line"
done
echo "\\_${underscores}_/"
