#! /bin/bash
. $NICOSVENV/bin/activate
echo $PATH
set +e

PYFILESCHANGED=$(~/tools2/bin/changedfiles --py)
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
