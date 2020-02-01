# -*- mode: ruby -*-
# vi: set ft=ruby :

["vagrant-disksize", "vagrant-reload", "vagrant-vbguest"].each do |plugin|
  unless Vagrant.has_plugin?(plugin)
    system("vagrant plugin install #{plugin}")
  end
end

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |v|
    v.gui = false
  end

  config.vm.define "sender", primary: true do |sender|
    sender.vm.network "private_network", ip: "192.168.33.10"
    sender.vm.hostname = "sender"
    sender.vm.provision "shell", run: "always", inline: "sudo route del default"
    sender.vm.provision "shell", run: "always", inline: "sudo route add default gw 192.168.33.100"
  end

  config.vm.define "receiver" do |receiver|
    receiver.vm.network "private_network", ip: "192.168.66.11"
    receiver.vm.hostname = "receiver"
    receiver.vm.provision "shell", run: "always", inline: "sudo route del default"
    receiver.vm.provision "shell", run: "always", inline: "sudo route add default gw 192.168.66.201"
  end

  config.vm.define "router1" do |router1|
    router1.vm.network "private_network", ip: "192.168.33.100"
    router1.vm.network "private_network", ip: "192.168.50.101"
    router1.vm.hostname = "router1"
    router1.vm.provision "shell", run: "always", inline: "sudo route add -net 192.168.66.0/24 gw 192.168.50.200 dev enp0s9"
    router1.vm.provision "shell", run: "always", inline: "sudo sysctl -w net.ipv4.ip_forward=1"
  end

  config.vm.define "router2" do |router2|
    router2.vm.network "private_network", ip: "192.168.66.201"
    router2.vm.network "private_network", ip: "192.168.50.200"
    router2.vm.hostname = "router2"
    router2.vm.provision "shell", run: "always", inline: "sudo route add -net 192.168.33.0/24 gw 192.168.50.101 dev enp0s9"
    router2.vm.provision "shell", run: "always", inline: "sudo sysctl -w net.ipv4.ip_forward=1"
  end

  config.vm.box = "ubuntu/bionic64"
  config.disksize.size = '50GB'

  config.vm.provision :shell, path: "scripts/provision.bash"
  config.vm.provision :reload

  if File.directory? "../juniper-linux"
    config.vm.synced_folder "../juniper-linux", "/linux"
  elsif File.directory? "../linux"
    config.vm.synced_folder "../linux", "/linux"
  end
end
