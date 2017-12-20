#!/bin/bash
set +x
. $NICOSVENV/bin/activate
echo $PATH
set -x
export doc_changed=$(git diff --name-status `git merge-base HEAD HEAD^` | sed -e '/^D/d' | sed -e 's/.\t//' | grep doc)
if [[ -n "$doc_changed" ]]; then

    cd doc
    make html
    make latexpdf
else
    echo 'no changes in doc/'
fi
