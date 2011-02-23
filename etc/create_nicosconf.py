#!/usr/bin/env python

import sys, glob

rootdir, sysuser, sysgroup, nethost = sys.argv[1:5]

pythonpath = ':'.join(glob.glob('/opt/taco/lib/python*'))

print '''\
[nicos]
# Set the control path here.
# It should have subdirectories "setup", "log" and "run".
control_path = %(rootdir)s
# Set the path to the nicos-* scripts here.
bin_path = %(rootdir)s/bin
# The system user to use for daemons.
user = %(sysuser)s
# The system group to use for daemons.
group = %(sysgroup)s

[environment]
# Add additional environment variables here.
PYTHONPATH = %(pythonpath)s
NETHOST = %(nethost)s
''' % locals()
