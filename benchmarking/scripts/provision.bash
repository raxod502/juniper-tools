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
libpcap-dev
python3-dev
python3-pip
"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y $(grep -v "^#" <<< "$packages")
# No need to remove /var/lib/apt/lists as we're not building a Docker
# image.

pip3 install scapy==2.4.3
pip3 install pypcap==1.2.3 # TODO: remove this if pcapy works better
pip3 install pcapy

# Try to be idempotent.
if ! grep "source /vagrant/scripts/profile.bash" /home/vagrant/.bashrc &>/dev/null; then
    cat <<"EOF" >> /home/vagrant/.bashrc
if [ -f /vagrant/scripts/profile.bash ]; then
    source /vagrant/scripts/profile.bash
else
    echo "warning: Juniper shell profile not available" >&2
fi
EOF
fi
