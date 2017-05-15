
## Install all needed drivers and Ethereum mining software
## Required Ubuntu 16.04

wget https://developer.nvidia.com/compute/cuda/8.0/Prod2/local_installers/cuda-repo-ubuntu1604-8-0-local-ga2_8.0.61-1_amd64-deb
sudo dpkg -i cuda-repo-ubuntu1404_7.5-18_amd64.deb
sudo apt-get https://github.com/Genoil/cpp-ethereum/blob/master/README.md -y install software-properties-common
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install -y libcryptopp-dev libleveldb-dev libjsoncpp-dev libjsonrpccpp-dev libboost-all-dev libgmp-dev libreadline-dev libcurl4-gnutls-dev ocl-icd-libopencl1 opencl-headers mesa-common-dev libmicrohttpd-dev
sudo apt-get install git cmake  build-essential cuda -y
git clone https://github.com/Genoil/cpp-ethereum/
cd cpp-ethereum/
mkdir build
cd build
cmake -DBUNDLE=cudaminer ..
make -j4

## Test that Nvidia drivers are installed correctly



nvidia-smi

## Begin mining ETC and submitting to nanopool (as an example pool)
geth account new
geth --rpc --rpccorsdomain localhost 2>> geth.log &
cd ethminer
./ethminer --farm-recheck 200 -G -S etc-us-east1.nanopool.org:19999 -O 114cb26b220cba60630cbf1825916fcb88a25949.worker5/someguy@email.com

