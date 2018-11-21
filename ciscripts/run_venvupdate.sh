#! /bin/bash
venvfull=$1
pbranch=$2
venv=${venvfull##*/}
. $venvfull/bin/activate
echo

echo "==== Developer dependencies ======"
pip install -r requirements-dev.txt 2>&1  > pip-dev-$venv-$pbranch.log
cat pip-dev-$venv-$pbranch.log
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
allcustreq=`find . -mindepth 2 -name requirements\*.txt`
for custreq in $allcustreq ; do
   pip install -r $custreq 2>&1 >> pip-custom-$venv-$pbranch.log
done
cat pip-custom-$venv-$pbranch.log
echo "=========="
