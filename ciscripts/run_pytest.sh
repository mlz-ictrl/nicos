#! /bin/bash
venv=$1
echo $venv
set +x
. $venv/bin/activate
set -x

# Do not try to run simple fits in scipy using parallelism
# (makes a difference on Rocky Linux, see issue #4871).
export OMP_NUM_THREADS=1

mkdir -p ~/test/testroot
export NICOS_TEST_ROOT=~/test/testroot
export TZ=Europe/Berlin
python -m pytest -v test
