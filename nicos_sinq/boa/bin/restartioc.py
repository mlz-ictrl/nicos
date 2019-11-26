#!/usr/bin/env python36
"""
  A little script which restarts an IOC. The script works with the
  assumption that the IOC is run via procServ with -x logout

  Mark Koennecke, November 2019
"""
import pexpect
import sys


if len(sys.argv) < 3:
    print('Usage:\n\trestartioc.py host:port prompt\n')
    sys.exit()

con = sys.argv[1].split(':')
host = con[0]
port = con[1]
prompt = sys.argv[2]

child = pexpect.spawn('telnet ' + host + ' ' + port)
child.sendline('')
child.expect(prompt)
child.sendline('exit')
child.expect(prompt)
child.sendline('logout')

sys.exit()
