#!/bin/bash
set -e

venvfull="$1"
pbranch="${2-default}"
venv=${venvfull##*/}
. $venvfull/bin/activate
pip install --upgrade pip
echo

echo "==== NICOS core dependencies ======"
pip install -r requirements.txt 2>&1 > pip-core-$venv-$pbranch.log
cat pip-core-$venv-$pbranch.log
echo

echo "==== NICOS GUI dependencies ======"
pip install -r requirements-gui.txt 2>&1 > pip-gui-$venv-$pbranch.log
cat pip-gui-$venv-$pbranch.log
echo

echo "==== NICOS optional dependencies ======"
pip install -r requirements-opt.txt 2>&1 > pip-opt-$venv-$pbranch.log
cat pip-opt-$venv-$pbranch.log
echo

echo "==== CUSTOM dependencies ======"
allcustreq=$(find . -mindepth 2 -maxdepth 4 -name requirements\*.txt | xargs)
for custreq in $allcustreq ; do
   pip install --upgrade --upgrade-strategy eager -r $custreq 2>&1 >> pip-custom-$venv-$pbranch.log
done
cat pip-custom-$venv-$pbranch.log
echo "=========="

echo "==== Developer dependencies ======"
# install this last to override pytest from astropy which is too old
pip install -r requirements-dev.txt 2>&1  > pip-dev-$venv-$pbranch.log
cat pip-dev-$venv-$pbranch.log
echo
