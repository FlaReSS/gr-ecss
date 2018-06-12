# gr-ecss


--------------------------------------------------------------------------------------------------------

HOW TO INSTALL NEW GROUP OF OOT BLOCKS:
(notice that "prefix" must be the same directory where is GNURADIO. The default PyBOMBS path is "prefix").
Run this commands in the main directory of the OOT group.

PyBOMBS instsallation:

source ~/prefix/setup_env.sh 
mkdir build 
cd build 
cmake -DCMAKE_INSTALL_PREFIX=~/prefix ../ 
make 
make test 
sudo make install 
sudo ldconfig 


apt-get installation: 

mkdir build 
cd build 
cmake 
make 
make test 
sudo make install  
sudo ldconfig 


--------------------------------------------------------------------------------------------------------

HOW TO TEST NEW GROUP OF OOT BLOCKS:
create a new folder/directory in the main directory of the OOT group (ex gr_ecss) named: "test log"
(in that folder will be put the log files)

the command to run the tests is (in the build dir):

make test

the command to run one specific test with more info is (in the build dir):

ctest -R qa_AGC -VV

