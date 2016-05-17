#!/bin/bash

workers="1 2 4 8 16"
tasks="10000 100000"

for w in $workers 
    do
    workdir="worker"$w
    cd $workdir
    for t in $tasks; do
  	for i in $(seq 1 $t)
 	    do
 	    echo "sleep 0" >> "0_"$t
        done
    done
    cd ..
done
