#! /bin/bash
. $NICOS3VENV/bin/activate
echo $PATH
set +e

PYFILESCHANGED=$(~/tools2/bin/changedfiles --py)
if [[ -n "$PYFILESCHANGED" ]] ; then
    set -o pipefail
    PYTHONPATH=.:${PYTHONPATH} isort -c --diff $PYFILESCHANGED | tee isort_all.txt
    res=$?
    set +o pipefail
else
    echo 'no python files changed'
    res=0
fi

set -e

exit $res
