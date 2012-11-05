#!/bin/bash

echo "building uis..."

cd ui
for file in *.ui
do
	outfile=ui_${file%\.ui}.h

	echo -e "${file} -> ${outfile}"
	uic ${file} -o ${outfile}
done
