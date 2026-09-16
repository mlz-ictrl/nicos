#!/bin/bash
set -e

venvfull="$1"
pbranch="${2-default}"
venv=${venvfull##*/}

maxnumpy="numpy<2"

. $venvfull/bin/activate
echo

echo "==== NICOS core+gui dependencies ======"
pip install -r requirements-all.txt 2>&1 > pip-core-$venv-$pbranch.log
cat pip-core-$venv-$pbranch.log
echo


echo "==== CUSTOM dependencies ======"
allcustreq=$(find . -mindepth 2 -maxdepth 4 -name requirements\*.txt | xargs)
for custreq in $allcustreq ; do
   # use this line again if custom deps cause incompatible updates
   #pip install --upgrade --upgrade-strategy eager -r $custreq 2>&1 >> pip-custom-$venv-$pbranch.log
   pip install  -r $custreq  "$maxnumpy" 2>&1 >> pip-custom-$venv-$pbranch.log
done
cat pip-custom-$venv-$pbranch.log
echo "=========="

