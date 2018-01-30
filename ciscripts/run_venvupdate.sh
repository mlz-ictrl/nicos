#! /bin/bash
venv=$1
. $venv/bin/activate
echo

echo "==== Developer dependencies ======"
pip install -r requirements-dev.txt 2>&1  > pip-dev-$venv.log
cat pip-dev-$venv.log
echo

echo "==== NICOS core dependencies ======"
pip install -r requirements.txt 2>&1 > pip-core-$venv.log
cat pip-core-$venv.log
echo

echo "==== NICOS GUI dependencies ======"
pip install -r requirements-gui.txt 2>&1 > pip-gui-$venv.log
cat pip-gui-$venv.log
echo

echo "==== NICOS optional dependencies ======"
pip install -r requirements-opt.txt 2>&1 > pip-opt-$venv.log
cat pip-opt-$venv.log
echo

echo "==== CUSTOM dependencies ======"
allcustreq=`find . -mindepth 2 -name requirements\*.txt`
for custreq in $allcustreq ; do
   pip install -r $custreq 2>&1 >> pip-custom-$venv.log
done
cat pip-custom-$venv.log
echo "=========="
