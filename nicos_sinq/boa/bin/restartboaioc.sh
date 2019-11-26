#!/usr/bin/env bash
install=`dirname "$0"`
source ${install}/pexpect/bin/activate
${install}/restartioc.py localhost:20000 "boa>"
