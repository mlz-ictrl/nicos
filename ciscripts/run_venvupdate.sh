#!/bin/bash
set -e

venvfull="$1"
pbranch="${2-default}"
venv=${venvfull##*/}
. $venvfull/bin/activate
echo

if [ -f /etc/system-release-cpe ] ; then
    if grep -qsi centos  /etc/system-release-cpe; then
        sed -i -e "s/PyTango>=8.1.7,<9.0.0;python_version<'3.0'/PyTango>=9;python_version<'3.0'/" requirements-opt.txt
    fi
fi


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
allcustreq=`find . -mindepth 2 -maxdepth 4 -name requirements\*.txt | xargs`
# filter out ESS requirements for the Py2 run
allcustreq=$(python - <<EOF
import sys
if sys.version_info[0] == 2:
    py3only = [
        "nicos_ess/",
        "nicos_sinq/",
    ]
    for fn in "$allcustreq".split():
        if all(p not in fn for p in py3only):
            print(fn)
else:
    print("$allcustreq")
EOF
)

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

