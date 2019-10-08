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

"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y $(grep -v "^#" <<< "$packages")
# No need to remove /var/lib/apt/lists as we're not building a Docker
# image.

urls="

# Can't use kernel 5.3 because <https://www.virtualbox.org/ticket/18783>
# still isn't merged and thus latest VirtualBox Guest Additions fail to
# compile with 5.3.x kernel mainline.
https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.2.19/linux-headers-5.2.19-050219_5.2.19-050219.201910050835_all.deb
https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.2.19/linux-headers-5.2.19-050219-generic_5.2.19-050219.201910050835_amd64.deb
https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.2.19/linux-image-unsigned-5.2.19-050219-generic_5.2.19-050219.201910050835_amd64.deb
https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.2.19/linux-modules-5.2.19-050219-generic_5.2.19-050219.201910050835_amd64.deb

"

wget -nv $(grep -v "^#" <<< "$urls")
dpkg -i *.deb
rm -f *.deb

# Try to be idempotent.
if ! grep "source /vagrant/scripts/profile.bash" /home/vagrant/.bashrc &>/dev/null; then
    cat <<"EOF" >> /home/vagrant/.bashrc
source /vagrant/scripts/profile.bash
EOF
fi
