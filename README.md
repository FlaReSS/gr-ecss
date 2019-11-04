#gr-ecss

##HOW TO INSTALL NEW GROUP OF OOT BLOCKS: (notice that "prefix" must be the same directory where is GNURADIO. The default PyBOMBS path is "prefix"). Run this commands in the main directory of the OOT group.

###PyBOMBS installation:

    source ~/prefix/setup_env.sh  
    mkdir build  
    cd build  
    cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../  
    make  
    make test  
    sudo make install  
    sudo ldconfig  

###apt-get installation:

    mkdir build   
    cd build  
    cmake ../
    make
    make test  
    sudo make install  
    sudo ldconfig  

###MAC OS X installation (from MacPort):

    mkdir build  
    cd build  
    cmake -DCMAKE_INSTALL_PREFIX=/opt/local/ ../  
    make  
    make test  
    sudo make install  

##HOW TO TEST NEW GROUP OF OOT BLOCKS
create a new folder/directory in the main directory of the OOT group (ex gr_ecss) named: "test log" (in that folder will be put the log files)

the command to run the tests is (in the build dir):

    make test   
    
the command to run one specific test with more info is (in the build dir):

    ctest -R qa_AGC -VV

if you want to install the OOT Module in an older version of GnuRadio Companion, for example 3.7.9, it is important to update the cmake file and make sure you have correctly installed the volk library: Build and install Volk

    cd ~
    wget http://libvolk.org/releases/volk-1.3.tar.gz
    tar -xzvf volk-1.3.tar.gz
    cd volk-1.3
    mkdir build && cd build
    cmake ..
    make
    sudo make install
    
    
##DEPENDENCIES

####wkhtmltopdf 0.12.1:

    sudo wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb
    sudo dpkg -i wkhtmltox_0.12.5-1.xenial_amd64.deb
####PDFKit:

    pip install pdfkit
