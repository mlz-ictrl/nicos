#! /bin/bash
venvfull=$1
pbranch=$2
venv=${venvfull##*/}
. $venvfull/bin/activate
echo

if [ -f /etc/system-release-cpe ] ; then
    if grep -qs Centos  /etc/system-release-cpe; then
        sed -i -e "s/PyTango>=8.1.7,<9.0.0;python_version<'3.0'/PyTango>=9;python_version<'3.0'/" requirements-opt.txt
    fi
fi


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
