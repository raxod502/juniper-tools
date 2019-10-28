#!/usr/bin/env bash

set -e
set -o pipefail

cd /tmp

packages="

# Fix VirtualBox clock skew, see:
# https://stackoverflow.com/a/21365600/3538165
ntp

"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y $(grep -v "^#" <<< "$packages")
# No need to remove /var/lib/apt/lists as we're not building a Docker
# image.

# Try to be idempotent.
if ! grep "source /vagrant/scripts/profile.bash" /home/vagrant/.bashrc &>/dev/null; then
    cat <<"EOF" >> /home/vagrant/.bashrc
source /vagrant/scripts/profile.bash
EOF
fi
