# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |v|
    v.gui = true
  end

  config.vm.define "sender" do |sender|  
    sender.vm.network "private_network", ip: "192.168.33.10"
  end
  config.vm.define "receiver" do |receiver|  
    receiver.vm.network "private_network", ip: "192.168.33.11"
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
