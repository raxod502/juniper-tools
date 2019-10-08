# Juniper Networks '19-20 tools and scripts

This repository has all of our code that isn't intended for inclusion
into the Linux kernel (for that, see
<https://github.com/raxod502/juniper-linux>).

## Setup

Install [Vagrant]:

    $ sudo apt-get install vagrant
    $ sudo pacman -S vagrant

Install Vagrant plugins:

    $ vagrant plugin install vagrant-vbguest vagrant-reload

Provision and start VM. It takes about 3.5 minutes on my machine:

    $ vagrant up

Starting the VM after it's already provisioned the first time will be
much faster.

## Development

Assuming that you had a directory named `linux` or `juniper-linux`
next to the `juniper-tools` repository, this will be visible within
the VM at `/linux`. Also, the `juniper-tools` repository will be
visible at `/vagrant`.

As a shorthand for running a `make` command inside `/vagrant`, you can
use `jmake`. As a shorthand for running a `make` command inside
`/linux`, you can use `lmake`. This works because the `bin`
subdirectory of this repository is added to `$PATH` within the VM.

### Make targets

Run `make help` for information on what you can do.
