#! /bin/bash
venv=$1
. $venv/bin/activate
pip install -r requirements-dev.txt
pip install -r requirements.txt
allcustreq=`find . -mindepth 2 -name requirements\*.txt`
for custreq in $allcustreq ; do
   pip install -r $custreq
done
