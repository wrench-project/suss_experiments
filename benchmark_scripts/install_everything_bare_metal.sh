# On Ubuntu

sudo apt update
sudo apt install -y libboost-program-options-dev
sudo apt install -y cmake
sudo apt install -y libboost-dev
sudo apt install -y libboost-program-options-dev 

wget --no-check-certificate https://framagit.org/simgrid/simgrid/-/archive/v3.34/simgrid-v3.34.tar.gz
tar -xf simgrid-v3.34.tar.gz
cd simgrid-v3.34
mkdir build
cd build
cmake ..
make -j48
sudo make install
cd ../..

wget https://github.com/nlohmann/json/archive/refs/tags/v3.11.2.tar.gz
tar -xzf v3.11.2.tar.gz
cd json-3.11.2/
mkdir build
cd build/
cmake ..
make -j48
sudo make install
cd ../..

git clone https://github.com/wrench-project/wrench.git
cd wrench
mkdir build
cd build
cmake ..
make -j48
sudo make install
cd ../..

git clone https://github.com/wrench-project/scheduling_using_simulation_simulator.git
cd scheduling_using_simulation_simulator
mkdir build
cd build
cmake ..
make -j48
sudo make install
cd ../..

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

git clone https://github.com/wrench-project/suss_experiments.git

