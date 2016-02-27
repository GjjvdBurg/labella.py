#!/bin/bash

for f in `ls *.py`;
do
	echo "python ${f}"
	python ${f}
done
