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
tshark

"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y $(grep -v "^#" <<< "$packages")
# No need to remove /var/lib/apt/lists as we're not building a Docker
# image.

# Make SSH allow passing environment variables (e.g. VM).
sudo sed -i 's/AcceptEnv .*/AcceptEnv */' /etc/ssh/sshd_config

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
