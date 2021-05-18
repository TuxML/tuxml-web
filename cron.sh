#!/bin/bash

path="/home/zprojet/tuxml-web"

if [ -d $path ]
then
    cd $path
    python3 -m views.ML.script
else
	echo "$path does not exists"
fi
