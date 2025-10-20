sudo apt update
sudo apt install -y build-essential cmake libtool autoconf automake swig

# 克隆并编译 libfann
git clone https://github.com/libfann/fann.git /tmp/fann
cd /tmp/fann
cmake -B build -S .
cd build
make -j$(nproc)
sudo make install
sudo ldconfig