#! /bin/bash
. $NICOS3VENV/bin/activate

tools/check-setups -o setupcheck.log -s nicos_*/*/setups nicos_*/*/guiconfig*.py || ((res++)) || /bin/true

# temporary: ignore CARESS related messages
sed -i -e '/CARESS/d' setupcheck.log

~/tools2/bin/sc2gerrit

exit $((res))
