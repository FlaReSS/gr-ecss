# gr-ecss
gr-ecss OOT module for GnuRadio

Updated to GNU Radio 3.8, documentation still needs to be updated. 

### HOW TO INSTALL GNURADIO
#### PyBOMBS installation:
It is recommended to install GnuRadio v3.7.13.5, since it is the latest version v3.7 update. In fact, the Gnuradio structure from version v3.8 has changed and therefore the OOT module's compatibility may not be guaranteed in the future versions. 

The commands below have been used successfully on Ubuntu 18.04. 
Please, rember to change "MYUSER" with your own user name.

    sudo pip install PyBOMBS
    pybombs auto-config
    pybombs recipes add gr-recipes git+https://github.com/gnuradio/gr-recipes.git
    pybombs recipes add gr-etcetera git+https://github.com/gnuradio/gr-etcetera.git
    mkdir /home/MYUSER/gnuradio
    pybombs config --package gnuradio gitrev v3.7.13.5
    pybombs prefix init /home/MYUSER/gnuradio/prefix -a myprefix -R gnuradio-default
    
### apt-get installation:
Through apt-get installation it is possible to install a stable version of gnuradio in a particularly simple way. Unfortunately, to date, both on Ubuntu 18.04 and on 16.04 the available versions are too obsolete (updated 07/11/2019). In fact, it is necessary to install at least the v3.7.12 version of GnuRadio in order to correctly use all the blocks.

If you want to install the OOT Module in an older version of GnuRadio Companion, for example 3.7.9, it is important to update the cmake file and make sure you have correctly installed the volk library: Build and install Volk. But some blocks will be not compatible (for example the gr-ecss demodulator block).

    cd ~
    wget http://libvolk.org/releases/volk-1.3.tar.gz
    tar -xzvf volk-1.3.tar.gz
    cd volk-1.3
    mkdir build && cd build
    cmake ..
    make
    sudo make install
    
## HOW TO INSTALL NEW GROUP OF OOT BLOCKS
(notice that "/home/MYUSER/gnuradio/prefix/" must be the same directory where is GnuRadio, please remember to change MYUSER with your own user name.
Run this commands in the main directory of the OOT group.

### PyBOMBS installation:

    source /home/MYUSER/gnuradio/prefix/setup_env.sh  
    mkdir build  
    cd build  
    cmake -DCMAKE_INSTALL_PREFIX=/home/MYUSER/gnuradio/prefix ../  
    make  
    make test  
    sudo make install  
    sudo ldconfig  

### apt-get installation:

    mkdir build   
    cd build  
    cmake ../
    make
    make test 
    sudo make install  
    sudo ldconfig  

### MAC OS X installation (from MacPort):

    mkdir build  
    cd build  
    cmake -DCMAKE_INSTALL_PREFIX=/opt/local/ ../  
    make  
    make test  
    sudo make install  

## HOW TO TEST NEW GROUP OF OOT BLOCKS
In the previuos section, the command "make test" already run all the qa tests of the OOT module. It is possible to run the command many times. Thus, inside the previously made directory "build", run the followig command:

    make test   
    
the command to run one specific test with more info is (in the build dir):

    ctest -R qa_AGC -VV

The test results will be in the folders "Results" and "Graphs" inside the "python" directory inside "build". 
Thus, to change directory run (in the build dir):

    cd python/Results

or

    cd python/Graphs
    
### FINAL REPORT PDF
It is also possible to generate a final report pdf containing all the run tests. (Remember to install all the dependencies before).
Thus, run the following command in the build directory:

    python ../python/final_report.py

Finally, the final report pdf will be in the "Final Report" folder inside the main directory of the OOT module.
So, to change directory run (in the build dir):

    cd ../Final Report

## DEPENDENCIES

#### wkhtmltopdf 0.12.1:

##### Ubuntu18.04:
    sudo wget https://builds.wkhtmltopdf.org/0.12.1.3/wkhtmltox_0.12.1.3-1~bionic_amd64.deb
    sudo dpkg -i wkhtmltox_0.12.1.3-1~bionic_amd64.deb
    sudo apt-get install -f
    sudo ln -s /usr/local/bin/wkhtmltopdf /usr/bin
    sudo ln -s /usr/local/bin/wkhtmltoimage /usr/bi

#### PDFKit:

    pip install pdfkit
    
## DOXYGEN PDF GENERATION

to generate the PDF version of the doxygen files, from the build folder inside the gr-ecss folder:

    cd /docs/doxygen/
    doxygen
    cd latex
    make
the file containing all the documentation will be named ¨refman.pdf¨.

a recent version of doxygen is needed:

    sudo apt-get install flex
    sudo apt-get install bison
    git clone https://github.com/doxygen/doxygen.git
    cd doxygen
    mkdir build
    cd build
    cmake -G "Unix Makefiles" ..
    make
    sudo make install
    sudo ldconfig

additional packets for latex generation:

    sudo apt-get install texlive-font-utils
    sudo apt install texlive-latex-extra
