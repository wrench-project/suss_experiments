FROM amd64/ubuntu:jammy

MAINTAINER Henri Casanova <henric@hawaii.edu>

# add repositories
RUN apt-get update

# set timezone
RUN echo "America/Los_Angeles" > /etc/timezone && export DEBIAN_FRONTEND=noninteractive && apt-get install -y tzdata

# build environment
RUN apt-get -y install pkg-config git cmake cmake-data libboost-all-dev wget sudo curl zip vim

# install compiler
RUN apt-get -y install gcc g++

#################################################
# WRENCH's dependencies
#################################################

# set root's environment variable
ENV CXX="g++" CC="gcc"
WORKDIR /tmp

# install SimGrid
RUN git clone https://framagit.org/simgrid/simgrid.git && cd simgrid && git checkout dbb4b9d8b72ec01fe1748a7eb6b32222ffe3ece5 && mkdir build && cd build && cmake .. && make -j12 && sudo make install && cd ../.. && rm -rf simgrid


# install json for modern c++
RUN wget https://github.com/nlohmann/json/archive/refs/tags/v3.10.5.tar.gz && tar -xf v3.10.5.tar.gz && cd json-3.10.5 && cmake . && make -j4 && make install && cd .. && rm -rf v3.10.5* json-3.10.5

# install WRENCH
RUN git clone https://github.com/wrench-project/wrench.git  && cd wrench && git checkout a0ba28a8607eb6ed9855b1fb50bbcbd512ad7631 && cmake . && make -j4 && sudo make install && cd .. && rm -rf wrench

# clone and install the scheduling_with_simulations_simulator with the right commit tab
RUN git clone https://github.com/wrench-project/scheduling_using_simulation_simulator.git && cd scheduling_using_simulation_simulator && git checkout fcb4c7cb1daf2cc61fc15f761b206b7057a27a65 && mkdir build && cd build && cmake .. && make -j4 && sudo make install && cd ../.. && /bin/rm -rf scheduling_using_simulation_simulator/

# install pip
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py && /bin/rm get-pip.py

# install pymongo
RUN python3 -m pip install pymongo

# install matplotlib
#RUN python3 -m pip install matplotlib

#################################################
# Non-root user 'me'
#################################################

RUN useradd -ms /bin/bash me 
RUN adduser me sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER me
WORKDIR /home/me
RUN touch /home/me/.sudo_as_admin_successful

RUN git clone https://github.com/wrench-project/suss_experiments.git

