SHELL=/bin/sh

########################################
## User-facing Makefile variables

HEADLESS ?=
ROUTERS  ?=
MTU      ?=

########################################
## Check configuration and environment

ifneq (,$(wildcard /linux))
	LINUX := /linux
else ifneq (,$(wildcard ../../juniper-linux))
	LINUX := ../../juniper-linux
else ifneq (,$(wildcard ../../linux))
	LINUX := ../../linux
else
$(error linux source repository not available)
endif

ifneq (,$(wildcard /vagrant))
	REQUIRE_VM :=
	REQUIRE_HOST := echo "this command may only be run from the host" >&2; exit 1
else
	REQUIRE_HOST :=
	REQUIRE_VM := echo "this command may only be run from the VM" >&2; exit 1
endif

REQUIRE_SENDER := echo "this command may only be run from the sender VM" >&2; exit 1
REQUIRE_RECEIVER := echo "this command may only be run from the receiver VM" >&2; exit 1

HOSTNAME := $(shell hostname)
ifeq ($(HOSTNAME),sender)
	REQUIRE_SENDER :=
else ifeq ($(HOSTNAME),receiver)
	REQUIRE_RECEIVER :=
endif

ifeq (,$(ROUTERS))
	RECV_IP := 192.168.33.11
else
	RECV_IP := 192.168.66.11
endif

SSH_ARGS := -- -X

TSHARK := sudo tshark -T fields -e frame.number  -e _ws.col.Source \
	-e _ws.col.Destination -e _ws.col.Protocol -e icmp.type \
	-E header=y -e data.len -e _ws.col.Info \
	-f "host $(RECV_IP) and (icmp or tcp or udp)"

########################################
## Integrated documentation utilities

# Intentionally using lazy variable assignment here to support $@ in
# expansion.
MSG = (cat Makefile && echo "\#\#")			| \
	sed 's/^\#$$//'					| \
	sed -n '/^$(if $(CMD),$(CMD),$@): /,/\#\#/p'	| \
	sed '0,/^$$/d'					| \
	sed 's/^\# //'					| \
	head -n-1					| \
	sed 's/<VM>/$(if $(VM), VM=$(VM),)/g'		| \
	scripts/box.bash


help: ## Display this message
	@echo 'usage:' && (						\
		cat Makefile |						\
			nl -ba -nrz -s~ |				\
			grep ': [#]#' |					\
			sed -E 's/~(.+?): [#]# /~      make \1|/' |	\
			column -t -s'|' &&				\
		cat Makefile |						\
			nl -ba -nrz -s~ |				\
			grep '~[#]# ' |					\
			sed -E 's/[#]# (.+)/   \1:/'			\
	) |								\
		sort -n -k1 -t~ |					\
		sed -E 's/.+~//' |					\
		grep -E ' {6}' -m1 -B1 -A9999
	@$(MSG)

# Getting started: you probably want to begin by provisioning the VMs
# using 'make vm', then configuring the kernel with 'make configure'
# from one of the VMs.
#
# If you want to run tests that use intermediate routers, rather than
# just the source and destination machines, then you should 'export
# ROUTERS=yes' first. This is much slower as twice as many VMs must be
# provisioned, but it shows that the source and destination machines
# are really relying on ICMP Packet Reassembled rather than peeking at
# the link MTU directly.
#
# If you want to disable the graphical interface on the VMs, and avoid
# installing Wireshark into them, then you should 'export
# HEADLESS=yes' first. This is somewhat faster, but reduces
# debuggability and you won't be able to inspect network traffic.

msg: ## Show a post-command message (e.g. make msg CMD=clean)
	@$(MSG)

# You need to specify a command, e.g. 'make msg CMD=clean'.

########################################
## Manage VMs and virtual network

destroy: ## Destroy VM(s) and associated filesystem(s) (host-only)
	@$(REQUIRE_HOST)
	vagrant destroy -f $(VM) || true
	@$(MSG)

# The virtual machine has been destroyed. You may want to create and
# provision a new one with 'make vm'.

vm: ## Provision and boot one or both VMs (host-only)
	@$(REQUIRE_HOST)
	vagrant up $(VM)
	vagrant ssh $(VM) $(SSH_ARGS)
	@$(MSG)

# You can SSH back into the machine if you wish with 'make ssh<VM>'.

ssh: ## SSH into one VM (host-only)
	@$(REQUIRE_HOST)
	vagrant ssh $(VM) $(SSH_ARGS)
	@$(MSG)

# You can SSH back into the machine if you wish with 'make ssh<VM>'.

reboot: ## Reboot one or both VMs (host-only)
	@$(REQUIRE_HOST)
	vagrant reload $(VM)
	vagrant ssh $(VM) $(SSH_ARGS)
	@$(MSG)

# You can SSH back into the machine if you wish with 'make ssh<VM>'.

snapshot: ## Save a snapshot of one VM's state (host-only)
	@$(REQUIRE_HOST)
	vagrant snapshot push $(VM)
	@$(MSG)

# A snapshot has been saved of the current state of the VM. You can
# restore it at any time with 'make restore<VM>'. This may be
# desirable if you wish to reconfigure the kernel from scratch with
# destroying and re-provisioning the VM(s), because running 'make
# configure' on a VM that's already running the modified kernel will
# just replicate the same configuration that was already installed.

restore: ## Restore VM to original kernel (host-only)
	@$(REQUIRE_HOST)
	vagrant snapshot pop $(VM)
	@$(MSG)

# The latest VM snapshot was restored. If you did this so you can
# reconfigure the kernel from scratch, you may want to run 'make
# cleanall' from the host and then 'make configure' from the VM (see
# 'make ssh<VM>').

########################################
## Build and install Linux kernel

clean: ## Remove all Linux build artifacts, except config and editor files
	git -C $(LINUX) clean -ffdX -e "!/.config" -e "!/.dir-locals.el" -e "!/compile_commands.json"
	@$(MSG)

# Build artifacts have been removed. You may want to re-create them
# with 'make kernel'.

cleanall: ## Remove *all* Linux build artifacts, including config and editor files
	git -C $(LINUX) clean -ffdX
	@$(MSG)

# All build artifacts have been removed, including the kernel
# configuration and editor files. To run the kernel again, you will
# need to generate a new configuration. This can be done with 'make
# configure' from the VM (see 'make ssh', or 'make vm' if you've
# destroyed it).

# However, note that if you have already installed the modified kernel
# into the VM(s) and booted into it, then the 'make configure' command
# won't generate a new configuration; instead, it will just replicate
# the one for the kernel that was installed. This is probably fine,
# but if you wish to reconfigure from scratch, you will need to
# destroy and recreate the VM(s), using 'make destroy' and 'make vm'.

# Alternatively, if you used 'make snapshot' to take a snapshot of the
# VM(s) back before you installed and booted into the modified kernel,
# you can restore it using 'make restore', which removes the need to
# destroy and re-create the VM(s).

configure: ## Configure kernel (VM-only)
	@$(REQUIRE_VM)
	cat "/boot/config-$$(uname -r)" > $(LINUX)/.config
	make -C $(LINUX) olddefconfig
	yes "" | make -C $(LINUX) localmodconfig
	sed -i 's/CONFIG_LOCALVERSION=""/CONFIG_LOCALVERSION="-JUNIPER"/' $(LINUX)/.config
	@$(MSG)

# A configuration file has been generated. You may now wish to compile
# the kernel from the host machine (for performance) with 'make
# kernel'.

kernel: ## Compile kernel (host-only)
	@$(REQUIRE_HOST)
	make -C $(LINUX) olddefconfig
	time make -C $(LINUX) "-j$$((2 * $$(nproc)))"
	@$(MSG)

# The kernel has been compiled. You may now install it from the VM
# with 'make install' (see 'make ssh'). However, it may first be
# desirable to take a snapshot of the VM with 'make snapshot<VM>' so
# that you can later revert to it with 'make restore<VM>' if you wish.
# This is because if you decide you want to reconfigure the kernel
# from scratch, you can't do it after the modified kernel is already
# installed and running.

install: ## Install kernel (VM-only)
	@$(REQUIRE_VM)
	sudo make -C $(LINUX) INSTALL_MOD_STRIP=1 modules_install install -j$$(nproc)
	@$(MSG)

# The kernel has been installed. You may now want to run 'make
# reboot<VM>' from the host machine to switch over to the new kernel.

########################################
## Editor support

cdb: ## Create compilation database for editor code intelligence
	grep -qxF /compile_commands.json $(LINUX)/.git/info/exclude || \
		echo /compile_commands.json >> $(LINUX)/.git/info/exclude
	make clean
	bear make kernel
	mv compile_commands.json $(LINUX)/
	@$(MSG)

# A compilation database has been generated. This means that editors
# which use LLVM as a backend for code intelligence will be able to
# handle the kernel source code correctly. You may want to refer to
# the following article for background information on compilation
# databases:
#
# https://sarcasm.github.io/notes/dev/compilation-database.html

dirlocals: ## Create .dir-locals.el to configure Emacs for kernel development
	cp template/.dir-locals.el $(LINUX)/.dir-locals.el
	@$(MSG)

# A .dir-locals.el file has been generated. Now Emacs will use correct
# indentation and style settings for C source code in the kernel.

########################################
## Test implementation

wireshark: ## Launch Wireshark to inspect VM network traffic (VM-only)
	@$(REQUIRE_VM)
	sudo wireshark >/dev/null 2>&1 &
	@$(MSG)

# Wireshark should now be open on your host machine. If it's not,
# something has gone wrong with the X forwarding configuration.

tshark: ## Launch tshark to inspect VM network traffic (VM-only)
	@$(REQUIRE_VM)
	@if [ $(HOSTNAME) = sender -o $(HOSTNAME) = receiver ]; then\
		$(TSHARK) -i enp0s8;									\
	else														\
		$(TSHARK) -i enp0s9;									\
	fi

tcp: ## Initialize TCP connection (VM-only)
	@$(REQUIRE_VM)
	@if [ $(HOSTNAME) = receiver ]; then\
		nc -l 3000;							\
	elif [ $(HOSTNAME) = sender ]; then	 \
		nc $(RECV_IP) 3000;						\
	else									\
		echo "this can only be run from the sender or receiver" >&2;	\
		exit 1; 							\
	fi
	@$(MSG)

# Once you have initialized the TCP connection on both the sender and
# receiver, you may now wish to decrease the path MTU using 'make
# reduce'. (When testing without routers, this should be done on the
# sender and receiver; when testing with routers, it should be done
# only on the two routers.)

reduce: ## Reduce the path MTU (VM-only)
	@make mtu MTU=800
	@$(MSG)

# Once you have reduced the link MTUs on both sender and receiver
# (when testing without routers) or on both routers (when testing with
# routers), you may wish to send a large packet by pasting the
# contents of 'packet_data.txt' into netcat on the sender. To inspect
# network traffic when you do this, you may wish to run 'make
# wireshark' first, provided you are not running in headless mode.

reset: ## Reset the path MTU to its original value
	@make mtu MTU=1500
	@$(MSG)

# Once you have reset the link MTUs on both sender and receiver (when
# testing without routers) or on both routers (when testing with
# routers), you may wish to run another experiment via 'make tcp' and
# 'make reduce'.

mtu: ## Set the path MTU to any value (e.g. make mtu MTU=400) (VM-only)
	@$(REQUIRE_VM)
	@if [ \( $(HOSTNAME) = receiver -o $(HOSTNAME) = sender \) -a -z $(ROUTERS) ]; then\
		sudo ip link set mtu $(MTU) dev enp0s8;\
	elif [ $(HOSTNAME) = sender-router -a -n $(ROUTERS) ]; then\
		sudo ip link set mtu $(MTU) dev enp0s9;\
		sleep 3;\
		sudo route add -net 192.168.66.0/24 gw 192.168.50.200 dev enp0s9;\
	elif [ $(HOSTNAME) = receiver-router -a -n $(ROUTERS) ]; then\
		sudo ip link set mtu $(MTU) dev enp0s9;\
		sleep 3;\
		sudo route add -net 192.168.33.0/24 gw 192.168.50.101 dev enp0s9;\
	elif [ -z $(ROUTERS) ]; then \
		echo "this can only be run from the sender or receiver" >&2;\
		exit 1;\
	else\
		echo "this can only be run from the intermediate routers" >&2;\
		exit 1;\
	fi

check: ## Check the path MTU cache (VM-only, sender-only)
	@$(REQUIRE_VM)
	@$(REQUIRE_SENDER)
	ip route get to $(RECV_IP)

clear: ## Clear the path MTU cache (VM-only, sender-only)
	@$(REQUIRE_VM)
	@$(REQUIRE_SENDER)
	sudo ip route flush cache to $(RECV_IP)
	@$(MSG)

# The path MTU cache has been cleared, as you can see by running 'make
# check'. You may wish to restart the experiment by running 'make
# reset' on the routers (when testing with routers) or sender and
# receiver (when testing without routers).

########################################
## Inspect patch

patch: ## Genenerate and show Git diff of all Juniper kernel changes
	git -C $(LINUX) diff $$(git -C $(LINUX) describe --tags --abbrev=0).. > juniper.patch
	git -C $(LINUX) diff $$(git -C $(LINUX) describe --tags --abbrev=0)..
	@$(MSG)

# The patch has been saved to 'juniper.patch'.
