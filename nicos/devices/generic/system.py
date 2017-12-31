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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""System-related device classes for NICOS."""

import os
import ctypes

from nicos import session
from nicos.core import Readable, Param, Override, status, none_or
from nicos.core.errors import NicosError, ConfigurationError

units = {'B': 1,
         'KiB': 1024.,
         'MiB': 1024. ** 2,
         'GiB': 1024. ** 3,
         'TiB': 1024. ** 4,
         'PiB': 1024. ** 5,
        }


class FreeSpace(Readable):
    """This is a readable device that returns the free space on a filesystem.

    It is useful to record this in the cache, for example to enable warnings
    about low free space before data files cannot be saved anymore.

    The device status is `OK` until free space is below the value set by the
    `minfree` parameter.
    """

    parameters = {
        'path':     Param('The path to the filesystem mount point (or "None" '
                          'to check the experiment data directory).',
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
            if os.name == 'nt':
                free = ctypes.c_ulonglong(0)
                ret = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(path), None, None, ctypes.pointer(free))
                if ret == 0:
                    raise OSError('GetDiskFreeSpaceExW call failed')
                return free.value / self._factor
            else:
                st = os.statvfs(path)
                return (st.f_frsize * st.f_bavail) / self._factor
        except OSError as err:
            raise NicosError(self, 'could not determine free space: %s' % err)

    def doStatus(self, maxage=0):
        free = self.read()
        munit = self.parameters['minfree'].unit
        mfactor = units.get(munit, (1024 ** 3))
        if free * self._factor < self.minfree * mfactor:
            return status.ERROR, 'free space %(free).2f %(unit)s below ' \
                '%(minfree).2f %(munit)s' \
                % {'free': free,
                   'minfree': self.minfree,
                   'unit': self.unit,
                   'munit': munit}
        return status.OK, '%.2f %s free' % (free, self.unit)

    def doUpdateMinfree(self, value):
        if self._cache:
            self._cache.invalidate(self, 'status')

    def doUpdateUnit(self, unit):
        factor = units.get(unit, None)
        if factor is None:
            raise ConfigurationError('Unsupported unit, allowed: %s' %
                                     ','.join(units))
        self._factor = factor
