#! /bin/bash
venv=$1
echo $venv
set -e
set +x
. $venv/bin/activate
set -x
set +e

PYFILESCHANGED=$(~/tools2/bin/changedfiles --py)

# filter out ESS code for the Py2 run
PYFILESCHANGED=$(python - <<EOF
import sys
if sys.version_info[0] == 2:
    for fn in "$PYFILESCHANGED".split():
        if "nicos_ess/" not in fn and "nicos_sinq/" not in fn:
            print(fn)
else:
    print("$PYFILESCHANGED")
EOF
)

if [[ -n "$PYFILESCHANGED" ]] ; then
    set -o pipefail
    PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc $PYFILESCHANGED | tee pylint_all.txt
    res=$?
    set +o pipefail
else
    echo 'no python files changed'
    res=0
fi

set -e

~/tools2/bin/pylint2gerrit

exit $res
