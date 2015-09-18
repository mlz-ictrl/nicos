#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

import subprocess

from nicos.core import Readable, NicosError, status
from nicos.pycompat import urllib


class RadMon(Readable):

    def doInit(self, mode):
        h = urllib.HTTPBasicAuthHandler()
        h.add_password(realm='Administrator or User',
                       uri='http://miracam.mira.frm2/IMAGE.JPG',
                       user='rgeorgii', passwd='rg.frm2')
        self._op = urllib.build_opener(h)

    def doRead(self, maxage=0):
        img = self._op.open('http://miracam.mira.frm2/IMAGE.JPG').read()
        open('/tmp/radmon.jpg', 'wb').write(img)
        p1 = subprocess.Popen('/usr/local/bin/ssocr -d 3 -i 2 -t 40 '
                              'rotate 268 crop 298 192 55 34 '
                              'make_mono invert opening 1 '
                              '/tmp/radmon.jpg'.split(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen('/usr/local/bin/ssocr -d 1 -i 2 -t 40 '
                              'rotate 268 crop 387 158 23 30 '
                              'make_mono invert opening 1 '
                              '/tmp/radmon.jpg'.split(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out1, err1 = p1.communicate()
        out2, err2 = p2.communicate()
        out1 = out1.strip()
        out2 = out2.strip()
        if err1:
            raise NicosError(self, 'ERROR in mantissa')
        if err2:
            raise NicosError(self, 'ERROR in exponent')
        return 0.01 * float(out1 + b'e-' + out2) * 1e6  # convert to uSv/h

    def doStatus(self, maxage=0):
        return status.OK, ''
