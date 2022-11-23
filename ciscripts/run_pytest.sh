#! /bin/bash
venv=$1
echo $venv
set +x
. $venv/bin/activate
set -x

mkdir -p ~/test/testroot
export NICOS_TEST_ROOT=~/test/testroot
export TZ=Europe/Berlin
python -m pytest -v test
