#! /bin/bash
. $NICOS3VENV/bin/activate

tools/check-setups -o setupcheck.log -s $(shell find . -mindepth 3 -type d -name setups) $(shell find . -name guiconfig.py) || ((res++)) || /bin/true

# temporary: ignore CARESS related messages
sed -i -e '/CARESS/d' setupcheck.log

~/tools2/bin/sc2gerrit

exit $((res))
