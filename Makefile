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

destroy: ## Destroy VM and associated filesystem (host-only)
	@$(REQUIRE_HOST)
	vagrant destroy -f

vm: ## Bring up VM and SSH into it (host-only)
	@$(REQUIRE_HOST)
	vagrant up
	vagrant ssh

clean: ## Remove all Linux build artifacts, including config
	git -C $(LINUX) clean -ffdX

configure: ## Configure kernel (VM-only)
	@$(REQUIRE_VM)
	cat "/boot/config-$$(uname -r)" > $(LINUX)/.config
	make -C $(LINUX) olddefconfig
	sed 's/CONFIG_LOCALVERSION=""/CONFIG_LOCALVERSION="-JUNIPER"/' < $(LINUX)/.config > /tmp/.config
	mv /tmp/.config $(LINUX)/.config

kernel: ## Compile kernel (host-only)
	@$(REQUIRE_HOST)
	make -C $(LINUX) olddefconfig
	time make -C $(LINUX) "-j$$(nproc)"

install: ## Install kernel (VM-only)
	@$(REQUIRE_VM)
	sudo make -C $(LINUX) INSTALL_MOD_STRIP=1 modules_install install

reboot: ## Reboot VM (host-only)
	@$(REQUIRE_HOST)
	vagrant reload
	vagrant ssh
