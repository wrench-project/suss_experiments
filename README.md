# Reproducible Research for JSSPP Journal submission

This repository contains data, scripts, and code for making the research in the
_On the Feasibility of Simulation-driven Portfolio Scheduling for
Cyberinfrastructure Runtime Systems_ manuscript by McDonald et al. 
(submitted for publication to JPDC) reproducible.

All result plots used in the manuscript (and others that were omitted due to lack of space) are
available in the `./plot_analyze_results/plots_v3/` directory. The content below details all the steps
to generate these plots, which entails running simulations, storing simulation output in a database, 
extracting results from this database, and analyzing/plotting the results, all using Python
scripts included in this repository. 

## Running all simulations

Complete experimental results are provided as a MongoDB dump in `./raw_data/dump.tgz`, and importing
these results into a locally running MongoDB can be done easily as: 
```
cd ./raw_data/
tar -xzf dump.zip
mongorestore
```
If you _really_ want to re-run everything, follow the steps below.  Otherwise, skip to the next section. 

### Step 1: Install the simulator code (in a Docker)

The simulator is hosted in [another
repository](https://github.com/wrench-project/scheduling_using_simulation_simulator).
All experiments are conducted with the simulator's code in its main branch (commit tag
`ed177407915117a57bf6ede5e166553abdda0900`). 

A [Dockerfile](https://docs.docker.com/) image with the simulator installed in
`/usr/local/bin/scheduling_using_simulation_simulator` can be built from the [Dockerfile](https://docs.docker.com/engine/reference/builder/) in
`./simulator/Dockerfile`.

To build the Docker image from this Docker file, invoke the following command in the top directory of this repository: 
```
docker build --no-cache -t jsspp_journal ./simulator/
```

### Step 2: Workflow JSON files

All JSON workflow description files, which are [WfCommons instances](https://wfcommons.org/instances), are available in the `./workflows/` directory.  Nothing to do here. 

### Step 3: Setup Mongo

The subsequent steps requires that a `mongod` daemon be started locally, so
that simulation output can be stored to and read from a MongoDB.   Here is 
a typical way to start a `mongod` that stores its data in directory `/tmp/db`

```
mkdir /tmp/db
mongod --dbpath /tmp/db 
```

### Step 4: Run all simulations

A script to run all simulations is available in `./run_script/run_all_simulations.py`. This script takes as input a data version number, a MongoDB URL, 
a number of threads to use, a list of platform configurations to use, a list of workflow configurations to use, and then a sequence of arguments that 
describe the experiments to run. For instance, the command-line below would run all experiments for producing all the data used in the manuscript
on 32 cores and store the simulation results in a MongoDB that runs on localhost. 

```
cd ./run_scripts
./run_all_simulations.py v3 mongodb://localhost .. 32 0,1,2 0,1,2,3,4,5,6,7,8 --run-ideal --run-ideal-multi-adaptation --run-noise 1000 1099
```

Several instances of the script can be started on multiple machines to parallelize the execution further, provided the MongoDB can be
accessed remotely.


## Extracting and post-processing raw simulation output from MongoDB

A script to extract and post-process simulation output data from MongoDB 
is available in `./extract_script/extract_all_results.py`. This script takes as
argument a version string and a MongoDB URL. For instance, to extract all
results from a locally running MongoDB, it could be invoked as:

```
cd ./extract_scripts
./extract_all_results.py v3 mongodb://localhost
```

The script generates several `*.dict` files in the `./extract_scripts` directory. These files are provided in this repository,
so that you do not have to re-generate them. 

## Plotting/analyzing the simulation output

Scripts to plot/analyze extracted simulation output data are available in
the `./plot_scripts/` directory.  These scripts must be invoked from that directory, read in the `*.dict`
files in the `./extract_scripts/` directory, and generate `.pdf` plots and
text output, which are the basis for all presented simulation results and/or plots in the
paper. These scripts take in a version string. For instance, running the following command
in the `./plot_scripts` directory will produce **all** output:

```
cd ./plot_analyze_results_scripts
./plot_all_results.py v3
```

Text output is displayed in the terminal, and PDF files are generated in a created `./plot_analyze_results_scripts/plots_v3` directory. These files
are included in this repository, so that you do not have to re-generate them. 

---
