#!/usr/bin/env python

import sys, glob

sysuser, sysgroup, nethost, setup = sys.argv[1:5]

pythonpath = ':'.join(glob.glob('/opt/taco/lib*/python*/site-packages'))


print '''\
[nicos]
# The system user to use for daemons.
user = %(sysuser)s
# The system group to use for daemons.
group = %(sysgroup)s
# The path to the instrument setup files.
setups_path = %(setup)s

[environment]
# Add additional environment variables here.
PYTHONPATH = %(pythonpath)s
NETHOST = %(nethost)s
''' % locals()
