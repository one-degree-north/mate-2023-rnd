#!/bin/bash

if (( $EUID != 0 )); then
    echo "use sudo"
    exit
fi

echo "installing libraries..."
apt install -y i2c-tools libi2c-dev

echo "initializing repo..."
git clone https://github.com/fm4dd/pi-bno055
cd pi-bno055

echo "compiling pi-bno055..."
make -j3

echo "moving things around..."
chmod +x ./getbno055
cp ./getbno055 /usr/bin/getbno055

echo "done!"
