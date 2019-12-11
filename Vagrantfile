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

  # 3 VM config copied from this website, which links to this repo
  # https://www.lab-time.it/2017/11/07/networking-labs-with-vagrant/
  # https://github.com/jwdevos/vagrant-networking-demo/blob/master/3-nodes-ubuntu/Vagrantfile

  config.vm.define "sender", primary: true do |sender|
    sender.vm.network "private_network", ip: "192.168.33.10"
    sender.vm.hostname = "sender"
    sender.vm.provision "shell", run: "always", inline: "route del default"
    sender.vm.provision "shell", run: "always", inline: "route add default gw 192.168.33.200"
  end

  config.vm.define "router" do |router|
    router.vm.network "private_network", ip: "192.168.33.200"
    router.vm.network "private_network", ip: "192.168.34.200"
    router.vm.hostname = "router"
    # router.vm.provision "shell", run: "always", inline: "route del default"
    router.vm.provision "shell", inline: "sudo sysctl -w net.ipv4.ip_forward=1"
  end

  config.vm.define "receiver" do |receiver|
    receiver.vm.network "private_network", ip: "192.168.34.10"
    receiver.vm.hostname = "receiver"
    receiver.vm.provision "shell", run: "always", inline: "route del default"
    receiver.vm.provision "shell", run: "always", inline: "route add default gw 192.168.34.200"
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
