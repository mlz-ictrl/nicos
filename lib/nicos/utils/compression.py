#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

"""Utilities for (de-)compressing files."""

import os
import zipfile
from os import path

from nicos import session

def zipFiles(zipfilename, rootdir):
    """Create a zipfile named <zipfile> containing all files from <rootdir> and therein

    returns the name of the created zipfile
    """
    if not zipfilename.endswith('.zip'):
        zipfilename = zipfilename + '.zip'
    zipfilename = path.abspath(zipfilename)
    zf = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED, True)
    nfiles = 0
    try:
        for root, _dirs, files in os.walk(rootdir):
            xroot = root[len(rootdir):].strip('/').strip('\\')
            for fn in files:
                zf.write(path.join(root, fn), path.join(xroot, fn))
                nfiles += 1
                if nfiles % 500 == 0:
                    session.log.info('%d files processed' % nfiles)
    finally:
        zf.close()
    return zipfilename


