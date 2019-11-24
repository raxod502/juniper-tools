# Juniper Networks '19-20 tools and scripts

This repository has all of our code that isn't intended for inclusion
into the Linux kernel (for that, see the
[juniper-linux](https://github.com/raxod502/juniper-linux)
repository).

## Setup

Fetch
[development](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/)
or
[stable](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/)
version of the Linux source repository and put it in a directory named
either `juniper-linux` or just `linux` next to the `juniper-tools`
repository. Check out the appropriate tag. I think the best one to use
would be v5.2.21 from the stable repository, as there are reports of
the 5.3 series being incompatible with VirtualBox Guest Additions.

Install [Vagrant](https://www.vagrantup.com/):

    $ wget -c https://releases.hashicorp.com/vagrant/2.2.4/vagrant_2.2.4_x86_64.deb; sudo dpkg -i vagrant_2.2.4_x86_64.deb
    $ sudo pacman -S vagrant

Install Vagrant plugins:

    $ vagrant plugin install vagrant-disksize vagrant-reload vagrant-vbguest

Provision and start VM. It takes about 3.5 minutes on my machine:

    $ vagrant up

I received an error about a Guest Addition version mismatch. See
[here](https://blog.patelify.com/posts/virtualbox-vagrant-the-version-mismatch-continues/)
for a solution. To find the VM UUID, run

    $ vboxmanage list vms

To restart a VM that is already running:

    $ vagrant reload [name|id]

Starting the VM after it's already provisioned the first time will be
much faster. Default password is "vagrant".

## Development

Assuming that you had a directory named `linux` or `juniper-linux`
next to the `juniper-tools` repository, this will be visible within
the VM at `/linux`. Also, the `juniper-tools` repository will be
visible at `/vagrant`.

As a shorthand for running a `make` command inside `/vagrant`, you can
use `jmake`. As a shorthand for running a `make` command inside
`/linux`, you can use `lmake`. This works because the `bin`
subdirectory of this repository is added to `$PATH` within the VM.

The machine is available locally at the virtual IP address
`192.168.33.10`.

### Make targets

Run `make help` for information on what you can do. Here's the general
workflow. If you want to clear things out from a previous run
(although this shouldn't be necessary unless something is messed up),
run

    $ make clean

to remove the kernel build artifacts from your source repository and
run

    $ make destroy

to remove the VMs and their filesystems, so everything will be
re-provisioned next time.

Then, to get started, run

    $ make vm

to provision both the sender and receiver VMs. Once they are booted,
select one of them and SSH into it by running

    $ make ssh [VM=sender | VM=receiver]

(the default is `sender` if you omit the `VM` argument). At this
point, it is time to build the kernel. This requires three steps:
configure, compile, and install. The first step must be done from
inside a VM because the configuration script needs to look at the
running VM and determine which modules must be built to support our
use case. Run:

    $ make configure

Then, from the host machine (otherwise it will be much slower), run:

    $ make kernel

Finally, from within each VM that you want to update, run:

    $ make install

In order to boot from the newly installed kernel, restart the VMs
using:

    $ make reboot

## Compilation cache

It is recommended that you install [ccache](https://ccache.dev/) and
add its binary directory to your `$PATH`, so that `gcc` resolves to
for example `/usr/lib/ccache/bin/gcc`. It is also recommended to
increase the maximum cache size using

    $ ccache --set-config=max_size=100.0G
