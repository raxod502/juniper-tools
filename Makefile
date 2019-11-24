ifneq (,$(wildcard /linux))
	LINUX := /linux
else ifneq (,$(wildcard ../juniper-linux))
	LINUX := ../juniper-linux
else ifneq (,$(wildcard ../linux))
	LINUX := ../linux
else
$(error linux source repository not available)
endif

ifneq (,$(wildcard /vagrant))
	CONTEXT := VM
	OTHER_CONTEXT := host
	VM := true
	REQUIRE_VM :=
	HOST :=
	REQUIRE_HOST := echo "this command may only be run from the host" >&2; exit 1
else
	CONTEXT := host
	OTHER_CONTEXT := VM
	HOST := true
	REQUIRE_HOST :=
	VM :=
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

help: ## Display this message
	@echo "usage (from the $(CONTEXT)):" >&2
	@grep -h "[#]# " $(MAKEFILE_LIST)	| \
		grep -v $(OTHER_CONTEXT)-only	| \
		sed 's/^/  make /'		| \
		sed 's/:[^#]*[#]# /|/'		| \
		column -t -s'|' >&2
	@echo >&2
	@echo "these commands are not available from the $(CONTEXT):" >&2
	@grep -h "[#]# " $(MAKEFILE_LIST)	| \
		grep $(OTHER_CONTEXT)-only	| \
		sed 's/^/  make /'		| \
		sed 's/:[^#]*[#]# /|/'		| \
		column -t -s'|' >&2

destroy: ## Destroy one or both VMs and associated filesystem(s) (host-only)
	@$(REQUIRE_HOST)
	vagrant destroy -f

vm: ## Provision and boot one or both VMs (host-only)
	@$(REQUIRE_HOST)
	vagrant up $(VM)
	vagrant ssh $(VM)

ssh: ## SSH into one VM (host-only)
	@$(REQUIRE_HOST)
	vagrant ssh $(VM)

clean: ## Remove all Linux build artifacts, except config and CDB
	git -C $(LINUX) clean -ffdX -e "!/.config" -e "!/compile_commands.json"

cleanall: ## Remove *all* Linux build artifacts, including config and CDB
	git -C $(LINUX) clean -ffdX

cdb: ## Create compilation database for code intelligence
	grep -qxF /compile_commands.json $(LINUX)/.git/info/exclude || \
		echo /compile_commands.json >> $(LINUX)/.git/info/exclude
	make clean
	bear make kernel
	mv compile_commands.json $(LINUX)/

configure: ## Configure kernel (VM-only)
	@$(REQUIRE_VM)
	cat "/boot/config-$$(uname -r)" > $(LINUX)/.config
	make -C $(LINUX) olddefconfig
	yes "" | make -C $(LINUX) localmodconfig
	sed -i 's/CONFIG_LOCALVERSION=""/CONFIG_LOCALVERSION="-JUNIPER"/' $(LINUX)/.config

kernel: ## Compile kernel (host-only)
	@$(REQUIRE_HOST)
	make -C $(LINUX) olddefconfig
	time make -C $(LINUX) "-j$$((2 * $$(nproc)))"

install: ## Install kernel (VM-only)
	@$(REQUIRE_VM)
	sudo make -C $(LINUX) INSTALL_MOD_STRIP=1 modules_install install -j$$(nproc)

reboot: ## Reboot one or both VMs (host-only)
	@$(REQUIRE_HOST)
	vagrant reload $(VM)
	vagrant ssh $(VM)

packet: ## Send large packet (VM-only, sender-only)
	@$(REQUIRE_VM)
	@$(REQUIRE_SENDER)
	scripts/send_lgpkt.bash 192.168.33.11
