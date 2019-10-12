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
	VM := true
	REQUIRE_VM :=
	HOST :=
	REQUIRE_HOST := echo "this command may only be run from the host" >&2; exit 1
else
	HOST := true
	REQUIRE_HOST :=
	VM :=
	REQUIRE_VM := echo "this command may only be run from the VM" >&2; exit 1
endif

help: ## Display this message
	@echo "usage:" >&2
	@grep -h "[#]# " $(MAKEFILE_LIST)	| \
		sed 's/^/  make /'		| \
		sed 's/:[^#]*[#]# /|/'		| \
		column -t -s'|' >&2

ssh: ## Bring up VM and SSH into it (host-only)
	@$(REQUIRE_HOST)
	vagrant up
	vagrant ssh

clean: ## Remove all Linux build artifacts, including config
	git -C $(LINUX) clean -ffdX

configure: ## Configure kernel (VM-only)
	@$(REQUIRE_VM)
	cat "/boot/config-$$(uname -r)" > $(LINUX)/.config
	make -C $(LINUX) olddefconfig
	sed 's/CONFIG_BUILD_SALT=""/CONFIG_BUILD_SALT="JUNIPER"/' < $(LINUX)/.config > /tmp/.config
	mv /tmp/.config $(LINUX)/.config

kernel: ## Compile kernel (host-only)
	@$(REQUIRE_HOST)
	make -C $(LINUX) olddefconfig
	time make -C $(LINUX) "-j$$(nproc)"
