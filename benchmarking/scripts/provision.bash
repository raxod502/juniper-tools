#!/usr/bin/env bash

set -e
set -o pipefail

cd /tmp

packages="

# https://www.linux.com/tutorials/how-compile-linux-kernel-0/
bc
bison
build-essential
fakeroot
flex
git
libelf-dev
libssl-dev
ncurses-dev
xz-utils

# Fix VirtualBox clock skew, see:
# https://stackoverflow.com/a/21365600/3538165
ntp

# inspect packet traffic, for development & testing
wireshark

# scapy
python3-pip

# look at our data files
jq
"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y $(grep -v "^#" <<< "$packages")
# No need to remove /var/lib/apt/lists as we're not building a Docker
# image.

pip3 install scapy==2.4.3
