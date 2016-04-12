#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Cleans up Cache data files from stray NUL Bytes e.g. adter Harddisk crashes"""

import os

# search for files at CURRENT DIRECTORY and below
nullfiles = {}
for root, dirs, files in os.walk('.'):
    for fn in files:
        if fn.endswith('.bak'):
            continue
        full_fn = os.path.join(root,fn)
        with open(full_fn,'r') as f:
            data = f.read()
            if '\x00' in data:
                print full_fn
                nullfiles[full_fn] = data

# write backup files and cleaned files
for fn, data in nullfiles.items():
    with open(fn + '.bak', 'w') as f:
        f.write(data)
    with open(fn, 'w') as f:
        f.write(data.replace('\x00',''))
