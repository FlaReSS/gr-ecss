@echo off

if "%1" == "-make" (
	rmdir build /s /q
	mkdir build
	cd build
rem	cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../
    cmake -G "Ninja" -DCMAKE_INSTALL_PREFIX="%CONDA_PREFIX%\Library" -DCMAKE_PREFIX_PATH="%CONDA_PREFIX%\Library" -DGR_PYTHON_DIR="%CONDA_PREFIX%\Lib\site-packages" -Wno-dev ..   
	cmake --build .
	cd ..
	goto done
	)
if "%1" == "-test" (
	rmdir build /s /q
	mkdir build
	cd build
rem	cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../
    cmake -G "Ninja" -DCMAKE_INSTALL_PREFIX="%CONDA_PREFIX%\Library" -DCMAKE_PREFIX_PATH="%CONDA_PREFIX%\Library" -DGR_PYTHON_DIR="%CONDA_PREFIX%\Lib\site-packages" -Wno-dev ..   
	cmake --build . --target test
	cd ..
	goto done
	)
if "%1" == "-notest" (
	rmdir build /s /q
	mkdir build
	cd build
rem	cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../
	cmake -G "Ninja" -DCMAKE_INSTALL_PREFIX="%CONDA_PREFIX%\Library" -DCMAKE_PREFIX_PATH="%CONDA_PREFIX%\Library" -DGR_PYTHON_DIR="%CONDA_PREFIX%\Lib\site-packages" -Wno-dev ..   
	cmake --build . --target install
	cd ..
	goto done
	)
if "%1" == "-all" (
	rmdir build /s /q
	mkdir build
	cd build
rem	cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../
    cmake -G "Ninja" -DCMAKE_INSTALL_PREFIX="%CONDA_PREFIX%\Library" -DCMAKE_PREFIX_PATH="%CONDA_PREFIX%\Library" -DGR_PYTHON_DIR="%CONDA_PREFIX%\Lib\site-packages" -Wno-dev ..   
	cmake --build . --target test
	cmake --build . --target install
	cd ..
	goto done
	)
echo Please, specify between -make, -test, -notest, -all

:done