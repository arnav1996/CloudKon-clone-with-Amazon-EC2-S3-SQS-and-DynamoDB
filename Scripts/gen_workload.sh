#!/bin/bash


workers="1 2 4 8 16"
secs="10 1000 10000"
secs10=1000
secs1000=100
secs10000=10

for w in $workers 
    do
    workdir="worker"$w
    rm -rf $workdir
    mkdir $workdir
    cd $workdir
    for s in $secs; do
	val=$(eval echo \$secs$s)
	for i in $(seq 1 $w); do
	    for j in $(seq 1 $val); do
		echo "sleep $s" >> $s
	    done
	done
    done
    cd ..
done
