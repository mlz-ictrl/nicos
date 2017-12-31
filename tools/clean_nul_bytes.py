#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""Cleans up Cache data files from stray NUL Bytes e.g. after Harddisk crashes"""

from __future__ import print_function

import os

# search for files at CURRENT DIRECTORY and below
nullfiles = {}
for root, dirs, files in os.walk('.'):
    for fn in files:
        if fn.endswith('.bak'):
            continue
        full_fn = os.path.join(root,fn)
        with open(full_fn, 'rb') as f:
            data = f.read()
            if b'\x00' in data:
                print(full_fn)
                nullfiles[full_fn] = data

# write backup files and cleaned files
count = 0
for fn, data in nullfiles.items():
    count += 1
    with open(fn + '.bak', 'wb') as f:
        f.write(data)
    with open(fn, 'wb') as f:
        f.write(data.replace(b'\x00', b''))

if count:
    print('Wrote backup for %d changed file(s), please check '
          'and remove them if not needed.' % count)
    print('The find command is left as an exercise to the caller.')
