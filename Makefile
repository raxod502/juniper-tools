help: ## Display this message
	@echo "usage:" >&2
	@grep -h "[#]# " $(MAKEFILE_LIST)	| \
		sed 's/^/  make /'		| \
		sed 's/:[^#]*[#]# /|/'		| \
		column -t -s'|' >&2

configure: ## Configure kernel from VM distro
	cat "/boot/config-$$(uname -r)" > /linux/.config
	lmake olddefconfig

kernel: ## Compile kernel (for use inside VM)
	make -C /linux "-j$$(nproc)"
