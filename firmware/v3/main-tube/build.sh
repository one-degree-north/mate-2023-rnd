#!/bin/bash

rm -rf ./build
mkdir build
export PICO_SDK_PATH=~/pico-sdk
cd ./build
cmake ..
make -j6
