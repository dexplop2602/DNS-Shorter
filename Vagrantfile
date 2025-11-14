# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.synced_folder ".", "/vagrant", disabled: false
  config.vm.provision "shell", path: "bootstrap.sh"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 2
  end
end