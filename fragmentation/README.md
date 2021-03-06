# Juniper Networks '19-20 tools and scripts

This repository has all of our code that isn't intended for inclusion
into the Linux kernel (for that, see the
[juniper-linux](https://github.com/raxod502/juniper-linux)
repository).

[This document](doc/about.md) explains the problem that our project
solves, and how it does so.

## Setup

First you must acquire the Linux source code. This can be done in one
of two ways:

* Clone [juniper-linux](https://github.com/raxod502/juniper-linux) and
  check out the `juniper` branch.
* Clone either the
  [development](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/)
  or
  [stable](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/)
  version of the Linux source repository. Check out an appropriate tag
  (we used v5.2.21 from stable) and apply
  [`juniper.patch`](juniper.patch).

Place the Linux source repository in the same directory as this
repository, and name it either `linux` or `juniper-linux`.
Alternatively, if you have some other Linux source repository that
you'd like to use instead, you can export the `LINUX` environment
variable to point at it.

Install [Vagrant](https://www.vagrantup.com/). Here is how to do it on
macOS, Ubuntu/Debian, and Arch/Manjaro, respectively:

    $ brew cask install vagrant
    $ wget -c https://releases.hashicorp.com/vagrant/2.2.4/vagrant_2.2.4_x86_64.deb; sudo dpkg -i vagrant_2.2.4_x86_64.deb
    $ sudo pacman -S vagrant

Provided that you have the standard development utilities available
(e.g. Make, GCC, etc.), you are ready to go.

## Test procedure

You can run `make help` to get an overview of all the things you can
do with our code.

### Configuration

Configuration is done by environment variables (or, equivalently,
Makefile variables):

* `$ROUTERS`: if empty, then two VMs will be created and connected
  directly to each other in a virtual network to test ICMP Packet
  Reassembled. If non-empty, then four VMs will be created, with the
  two additional VMs acting as intermediate routers. This is slower
  because more VMs must be provisioned, but it proves that ICMP Packet
  Reassembled is really working, because neither the sender VM nor the
  receiver VM can see the link between the two routers when its MTU is
  reduced, so they can only find out via ICMP.
* `$HEADLESS`: if empty, then the VMs will be accessible via graphical
  ttys. This can be helpful for debugging, but might be annoying since
  windows are created in your desktop environment when the VMs are
  started. If non-empty, then Vagrant is instructed to disable the
  GUIs for the VMs.

**I recommend setting these environment variables in a file called
`.env` in the root directory of this repository. You can place lines
like `ROUTERS=yes`, `HEADLESS=` into it and they will be set
automatically in the Makefile. If you set the variables manually
instead, you will have to make sure to do it in every tty!**

### Setup

* Run `make vm` to provision all of the VMs.
* Run `make ssh` to connect to one of them (this also happens
  automatically after provisioning) and run `make configure` to
  generate a configuration for the Linux kernel based on what features
  are required for the VMs.
* Run `make kernel` from the host machine to compile the (modified)
  Linux kernel.
* If desired, run `make snapshot` to take a snapshot of one of the
  VMs, which you can later restore with `make restore` in case you
  want to generate a pristine configuration for the Linux kernel from
  a machine that isn't already running the modified kernel.
* Connect to each of the VMs (you can specify which one by e.g. `make
  ssh VM=receiver`) and run `make install` to install the kernel
  image. Of course this only needs to be done for the sender and
  receiver even if you have intermediate routers, because ICMP Packet
  Reassembled does not require the cooperation of intermediate
  routers except for their conformance to ICMP.
* From the host machine, run `make reboot` to get the modified kernel
  running on all the VMs.

### Test procedure

* Check that there is no data in the PMTU cache on the sender by
  running `make check`.
* Set up a TCP connection between the sender and receiver by running
  `make tcp` on *first* the receiver (to start listening) and *then*
  the sender (to connect). This should be done before adjusting any
  MTUs because TCP will set its MSS automatically at connection time.
* Reduce the MTU of the intermediate link by running `make reduce` on
  the sender and receiver (if testing without routers) or on the two
  routers (if testing with routers). To access the routers, run `make
  ssh VM=(sender-router|receiver-router)`.
    * *Note that setting the MTU of a link to the same value twice in
      a row will produce an error, `SIOCADDRT: File exists`. This does
      not mean things are broken; it just means that the MTU is
      already set to the desired value.*
* If desired, open Wireshark using `make wireshark` (or tshark using
  `make tshark`) on the sender.
* Paste the contents of `packet_data.txt` into the netcat session on
  the sender.
    * Observe that ICMP Packet Reassembled is transmitted back to the
      sender.
* Check that there is now updated data in the PMTU cache on the sender
  by running `make check` again.
* Paste more data into the netcat session on the sender.
    * Observe in Wireshark that ICMP Packet Reassembled is no longer
      sent.
* To reset, run `make reset` on the same machines that you ran `make
  reduce` on, and run `make clear_cache` on the sender.

### Cleanup

* Run `make clean` to remove build artifacts from the Linux kernel.
    * Run `make cleanall` to remove even the configuration, which will
      then need to be regenerated with `make configure`.
* Run `make destroy` to delete the VMs and their filesystems.

### Editor configuration

* Run `make cdb` to generate a `compile_commands.json` file for the
  Linux kernel, for use with C language servers. This requires that
  you install the [BEAR](https://github.com/rizsotto/Bear) utility,
  which is not otherwise required for the build.
* Run `make dirlocals` to generate a `.dir-locals.el` file to
  configure Emacs to edit Linux kernel source with the appropriate
  style settings.

## Debugging tips

Assuming that you had a directory named `linux` or `juniper-linux`
next to the `juniper-tools` repository, this will be visible within
the VM at `/linux`. Also, the `juniper-tools` repository will be
visible at `/vagrant`.

The virtual machines are accessible locally at virtual IP addresses
listed in the [`Vagrantfile`](Vagrantfile). You can connect to them
using SSH, with the default username and password (`vagrant` /
`vagrant`).

### Virtual network setup

All IP addresses are on the 192.168 prefix (see [RFC
1918](https://tools.ietf.org/html/rfc1918)).

For testing without routers:

    sender
    33.10 -->enp8s0

                      receiver
             enp8s0<-- 33.11

For testing with routers:

    sender
    66.10 -->enp8s0

                    sender_router
             enp9s0<-- 66.100
                       50.100 -->enp8s0

                                       receiver_router
                                 enp8s0<-- 50.101
                                           33.101 -->enp9s0

                                                              receiver
                                                     enp8s0<-- 33.11

## Compilation cache

It is recommended that you install [ccache](https://ccache.dev/) and
add its binary directory to your `$PATH`, so that `gcc` resolves to
for example `/usr/lib/ccache/bin/gcc`. It is also recommended to
increase the maximum cache size using

    $ ccache --set-config=max_size=100.0G
