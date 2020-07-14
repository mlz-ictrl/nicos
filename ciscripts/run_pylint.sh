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
    py3only = [
        "nicos_ess/",
        "nicos_sinq/",
        "nicos/devices/notifiers/slack.py",
    ]
    for fn in "$PYFILESCHANGED".split():
        if all(p not in fn for p in py3only):
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
