FROM wrenchproject/wrench:unstable

MAINTAINER Henri Casanova <henric@hawaii.edu>

USER root

# update repository list
RUN apt-get update

# install compiler (likely installed already though)
RUN apt-get -y install g++ gcc

# set timezone
RUN echo "America/Los_Angeles" > /etc/timezone && export DEBIAN_FRONTEND=noninteractive && apt-get install -y tzdata

# install basic things, just in case
RUN apt-get -y install vim pkg-config git cmake cmake-data wget sudo curl zip

# clone and install the scheduling_with_simulations_simulator with the right commit tab
RUN git clone https://github.com/wrench-project/scheduling_using_simulation_simulator.git && cd scheduling_using_simulation_simulator && git checkout ed177407915117a57bf6ede5e166553abdda0900 && mkdir build && cd build && cmake .. && make -j4 && sudo make install && cd ../.. && /bin/rm -rf scheduling_using_simulation_simulator/

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

RUN git clone https://github.com/wrench-project/jsspp_journal_experiments.git

