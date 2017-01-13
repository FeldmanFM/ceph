#!/bin/bash
cp $1 ~/
scp ~/$1 node1:~/
for i in 1 2 3 4 5
do
	scp ~/$1 node$i:/usr/share/scripts/
done 
