#!/usr/bin/bash

if [ "$EUID" -ne 0 ]        # check if your running as root
  then echo "[...] Please run as root."
  exit
fi

apt-get -qq install python python-pip
pip install requests simplekml

echo "[...] Now installed all packages..."
