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

"""Utilities for uploading files to a ftp-server."""

import time
from os import path
from ftplib import FTP
from hashlib import md5

from nicos.pycompat import to_utf8

#
# hard-coded constants
#
# made available by J.Pulz for internal access only
# files will be stored there for 30 days and automatically deleted.
# the wise man keeps a local copy....
#
FTP_SERVER = 'ftp.frm2.tum.de'
FTP_PORT = 21210
FTP_USER = 'nicd'
FTP_P = ''.join(map(chr, [78, 103, 115, 65, 57, 84, 98, 67]))


def ftpUpload(filename, logger=None):
    """Uploads the given file to an user-accessible location

    returns a http download link for download purposes.
    """
    # we like to obscure the data at least a little bit.
    subdir = md5(to_utf8(filename + str(time.time()))).hexdigest()
    basename = path.basename(filename)

    try:
        with open(filename, 'rb') as fp:
            ftp = FTP()

            ftp.connect(FTP_SERVER, FTP_PORT)
            ftp.login(FTP_USER, FTP_P)

            try:
                ftp.mkd(subdir)  # may raise if dir already exists. Should be rare!
            except Exception:
                pass
            ftp.cwd(subdir)

            ftp.storbinary('STOR %s' % basename, fp)

            ftp.quit()
            ftp.close()
    except Exception:
        if logger:
            logger.error('Uploading ftp-file failed! Please check config and '
                         'log files', exc=1)
        raise

    return 'http://ftp.frm2.tum.de/outgoing/mdata/%s/%s' % (subdir, basename)
