#!/bin/bash

# Check the number of arguments
if [ $# -ne 1 ]; then
    echo "Usage: $0 <serverURL:port>"
    exit 1
fi


./dispacher.py v4 $1 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-ideal
./dispacher.py v4 $1 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-noise 1000 1099
./dispacher.py v4 $1 ../.. 0,1,2 0,1,2,3,4,5,6,7,8,9 --run-noise 1000 1099 --run-mitigation
./dispacher.py v4 $1 ../.. 0,1,2 1,2,3,5,6,8 --run-ideal --no-contention-in-speculative-executions
./dispacher.py v4 $1 ../.. 0,1,2 1,2,3,5,6,8 --run-noise 1000 1099 --no-contention-in-speculative-executions