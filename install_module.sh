#!/bin/bash
# Script to install a module in gnuradio.
#run it in the main folder of the OOT module

if [ "$1" = "-make" ]; then
	rm -r build
	mkdir build
	cd build
	cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../
	make
	cd ..
elif [ "$1" = "-test" ]; then
	rm -r build
	mkdir build
	cd build
	cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../
	make
	make test
	cd ..
elif [ "$1" = "-notest" ]; then
	rm -r build
	mkdir build
	cd build
	cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../
	make
	make install
	sudo ldconfig
	cd ..
elif [ "$1" = "-all" ]; then
	rm -r build
	mkdir build
	cd build
	cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../
	make
	make test
	make install
	sudo ldconfig
	cd ..
else
	echo Please, specify between -make, -test, -notest, -all
fi
