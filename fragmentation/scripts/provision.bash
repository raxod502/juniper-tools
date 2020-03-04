#!/usr/bin/env bash

# Install the requisite packages into a Vagrant VM, and install our
# shell profile so that we start in the right working directory.

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
tshark

"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y $(grep -v "^#" <<< "$packages")
# No need to remove /var/lib/apt/lists as we're not building a Docker
# image.
