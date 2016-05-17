#!/bin/bash


mkdir Results

mkdir Results/Local

for thread in 1 2 4 8 16
do
	for time in 10 1000 10000
	do
		echo "Operation Performing for time "$time" ms, Thread : "$thread
		python Client.py -s Local -w worker$thread/$time -t $thread >> Client"_"$time"_"$thread.txt
			
		
		mv Client"_"$time"_"$thread.txt Results/Local
	done
done

