#!/usr/bin/bash

sudo su
which apt-get 2> /dev/null && {
	apt-get -qq install python python-pip
	pip install requests simplekml

	echo "[...] Now installed all packages..."
	exit
}
echo "[...] You do not have 'apt-get' installed..."
