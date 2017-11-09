#! /bin/bash
venv=$1
echo $venv
set +x
. $venv/bin/activate
set -x

pytest -v test
