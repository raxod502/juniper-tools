#!/usr/bin/env bash

set -e
set -o pipefail

# Word-wrap the given message and display it in an ASCII-art box.
# E.g.:
#
#  _______________
# /               \
# | Hello, world! |
# \_______________/

if (( $# != 1 )); then
    echo "usage: scripts/box.bash MSG" >&2
    exit 1
else
    # Word-wrap paragraphs.
    #
    # https://stackoverflow.com/a/7359879/3538165
    # https://stackoverflow.com/a/16198793/3538165
    message="$(echo -E "$1" | sed '/./,$!d' | sed '$a\' | fmt -w75)"
fi

# Compute the length of the longest line.
length="$(echo -E "$message" | awk '{ print length }' | sort -n | tail -1)"

# Get a printf specifier for padding with spaces to that width.
format="%-${length}s"

# Get a sequence of that many underscores and that many spaces.
spaces="$(printf "$format" "")"
underscores="$(printf "$format" "" | sed "s/./_/g")"

# Make the actual box.
echo " _${underscores}_ "
echo "/ ${spaces} \\"
echo -E "${message}" | while read -r line; do
    printf "| ${format} |\n" "$line"
done
echo "\\_${underscores}_/"
