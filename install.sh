#!/bin/bash

# not as root please
if [ $(id -u) -eq 0 ] && [ "$1" != "--force" ] ; then
	echo 'Running as root causes issues with pip';
	echo 'Please run again as a normal user';
	echo 'Use --force if you wish to proceed regardless';
	exit 1;
fi

# python and pip3
sudo apt-get -y install python3 python3-pip
# python dependency packages
pip3 install -r requirements.txt
# pyre dependency package from github
pip3 install https://github.com/zeromq/pyre/archive/master.zip
