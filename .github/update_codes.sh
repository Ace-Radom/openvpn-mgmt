#/bin/bash

cd $1
# enter install dir

if [ ! -d "openvpn-mgmt" ]; then
    git clone --recursive https://github.com/Ace-Radom/openvpn-mgmt.git
else
    cd openvpn-mgmt
    git fetch --all
    git reset --hard origin/main
    git submodule update --recursive
fi
