#!/bin/bash

cd ~/projects/drone/app
./bin/arduino-cli compile --fqbn arduino:avr:uno $1

if [ "$?" -eq "0" ]; then
	./bin/arduino-cli upload -t -p /dev/ttyUSB0 --fqbn arduino:avr:uno $1
else
	exit 1
fi
