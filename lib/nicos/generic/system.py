#  -*- coding: utf-8 -*-
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

"""System-related device classes for NICOS."""

__version__ = "$Revision$"

import os

from nicos import session
from nicos.core import Readable, Param, Override, status, none_or
from nicos.core.errors import NicosError

class FreeSpace(Readable):
    """This is a readable device that returns the free space on a filesystem.

    It is useful to record this in the cache, for example to enable warnings
    about low free space before data files cannot be saved anymore.

    The device status is `OK` until free space is below the value set by the
    `minfree` parameter.
    """

    parameters = {
        'path':     Param('The path to the filesystem mount point (or None to '
                          'check the experiment data directory',
                          type=none_or(str), default=None),
        'minfree':  Param('Minimum free space for "ok" status',
                          unit='GiB', default=5, settable=True),
    }

    parameter_overrides = {
        'unit':         Override(default='GiB', mandatory=False),
        'pollinterval': Override(default=300),  # every 5 minutes is sufficient
        'maxage':       Override(default=330),
    }

    def doRead(self, maxage=0):
        if self.path is None:
            path = session.experiment.dataroot
        else:
            path = self.path
        try:
            st = os.statvfs(path)
        except OSError, err:
            raise NicosError(self, 'could not determine free space: %s' % err)
        return (st.f_bsize * st.f_bavail) / (1024 * 1024 * 1024.)

    def doStatus(self, maxage=0):
        free = self.read()
        if free < self.minfree:
            return status.ERROR, 'free space %.2f GiB below %.2f GiB' \
                % (free, self.minfree)
        return status.OK, '%.2f GiB free' % free

    def doUpdateMinfree(self, value):
        if self._cache:
            self._cache.invalidate(self, 'status')
