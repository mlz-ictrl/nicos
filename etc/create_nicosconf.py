#!/usr/bin/env python

import sys, glob

sysuser, sysgroup, nethost, setups, services = sys.argv[1:5]

services = services or 'cache,poller'

pythonpath = ':'.join(glob.glob('/opt/taco/lib*/python*/site-packages'))


print '''\
[nicos]
# The system user to use for daemons.
user = %(sysuser)s
# The system group to use for daemons.
group = %(sysgroup)s
# The path to the instrument setup files.
setups_path = %(setups)s

[services]
# The list of daemons to start from the nicos-system init script.
services = %(services)s

[environment]
# Add additional environment variables here.
PYTHONPATH = %(pythonpath)s
NETHOST = %(nethost)s
''' % locals()
