#!/usr/bin/env python
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

import sys, glob, os

sysuser, sysgroup, nethost, setups, services, addvars = sys.argv[1:7]

services = services or 'cache,poller'
try:
    tacobase = os.environ['DSHOME']
except KeyError:
    tacobase = '/opt/taco'
pythonpath = ':'.join(glob.glob(tacobase + '/lib*/python*/site-packages'))
if not pythonpath:
    # set some working default, if the taco dir does not exist yet
    print sys.stderr, '''\
Warning: There seems to be no TACO installed in %s,
setting up a default anyway.

If TACO is installed in a non-standard place,
set DSHOME to point to this directory.''' % tacobase
    pyversion = sys.version_info
    pythonpath = ':'.join('/opt/taco/%s/python%1d.%1d/site-packages' %
                          (libdir, pyversion[0], pyversion[1])
                          for libdir in ['lib', 'lib64'])

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
# You can add directories to sys.path here...
PYTHONPATH = %(pythonpath)s
PAGER = cat
# Define a TACO database host
NETHOST = %(nethost)s
# Add additional environment variables here.
%(addvars)s
''' % locals()
