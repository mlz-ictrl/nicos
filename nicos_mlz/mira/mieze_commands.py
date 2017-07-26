#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""Commands for MIEZE operation."""

from nicos import session
from nicos.core import UsageError
from nicos.core.scan import Scan, ManualScan
from nicos.commands import usercommand
from nicos.commands.scan import _fixType, _handleScanArgs, _infostr, _ManualScan
from nicos.pycompat import integer_types, string_types
from nicos_mlz.mira.devices.mieze import MiezeMaster


class MiezeScan(Scan):
    """
    Special scan class for MIEZE scans.
    """

    def __init__(self, settings, devices, positions, firstmoves=None,
                 multistep=None, detlist=None, envlist=None, preset=None,
                 scaninfo=None, scantype=None):
        miezedev = session.getDevice('mieze', MiezeMaster)
        self._nsettings = 1
        self._notherdevs = len(devices)
        if settings is not None:
            if settings == '*' or settings == -1:
                settings = [sett['_name_'] for sett in miezedev.curtable]
            elif isinstance(settings, string_types + integer_types):
                settings = [settings]
            self._nsettings = len(settings)
            new_devices = devices + [miezedev]
            new_positions = []
            if not positions:
                # the msingle case
                new_positions.extend([sett] for sett in settings)
            for poslist in positions:
                new_positions.extend(poslist + [sett] for sett in settings)
            devices = new_devices
            positions = new_positions
        Scan.__init__(self, devices, positions, firstmoves, multistep,
                      detlist, envlist, preset, scaninfo, scantype)

    def beginScan(self):
        if self._notherdevs == 0:
            self.dataset.xindex = 1  # plot against tau
        Scan.beginScan(self)

    def preparePoint(self, num, xvalues):
        if num > 1 and self._nsettings > 1 and (num-1) % self._nsettings == 0:
            for sink in self._sinks:
                sink.addBreak(self.dataset)
        Scan.preparePoint(self, num, xvalues)


class MiezeManualScan(ManualScan):
    """
    Special scan class for MIEZE manual scans.
    """

    def __init__(self, settings, firstmoves=None, multistep=None, detlist=None,
                 envlist=None, preset=None, scaninfo=None, scantype=None):
        self.miezedev = session.getDevice('mieze', MiezeMaster)
        ManualScan.__init__(self, firstmoves, multistep, detlist, envlist,
                            preset, scaninfo, scantype)
        self._envlist.append(self.miezedev)
        if settings is not None:
            if settings == '*' or settings == -1:
                self.settings = [sett['_name_']
                                 for sett in self.miezedev.curtable]
            elif isinstance(settings, string_types + integer_types):
                self.settings = [settings]
            else:
                self.settings = settings
        else:
            self.settings = None

    def step(self, **preset):
        if self.settings is None:
            return ManualScan.step(self, **preset)
        for setting in self.settings:
            self.miezedev.move(setting)
            self.miezedev.wait()
            ManualScan.step(self, **preset)


class _MiezeManualScan(_ManualScan):
    def __init__(self, settings, args, kwargs):  # pylint: disable=W0231
        scanstr = _infostr('mmanualscan', (settings,) + args, kwargs)
        preset, scaninfo, detlist, envlist, move, multistep = \
            _handleScanArgs(args, kwargs, scanstr)
        self.scan = MiezeManualScan(settings, move, multistep, detlist,
                                    envlist, preset, scaninfo)


@usercommand
def mscan(settings, dev, *args, **kwargs):
    """MIEZE scan over device(s).

    First argument is a list of MIEZE settings or -1 to scan all settings.

    All other arguments are handled like for `scan`.
    """
    def mkpos(starts, steps, numsteps):
        return [[start + i*step for (start, step) in zip(starts, steps)]
                for i in range(numsteps)]
    scanstr = _infostr('mscan', (settings, dev) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(restargs, kwargs, scanstr)
    MiezeScan(settings, devs, values, move, multistep, detlist,
              envlist, preset, scaninfo).run()


@usercommand
def mcscan(settings, dev, *args, **kwargs):
    """MIEZE centered scan over device(s).

    First argument is a list of MIEZE settings or -1 to scan all settings.

    All other arguments are handled like for `scan`.
    """
    def mkpos(centers, steps, numperside):
        return [[center + (i-numperside)*step for (center, step)
                 in zip(centers, steps)] for i in range(2*numperside+1)]
    scanstr = _infostr('mcscan', (settings, dev) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(restargs, kwargs, scanstr)
    MiezeScan(settings, devs, values, move, multistep, detlist,
              envlist, preset, scaninfo).run()


@usercommand
def msingle(settings, *args, **kwargs):
    """Single MIEZE counting.

    First argument is a list of MIEZE settings or -1 to scan all setings.

    All other arguments are handled like for `count`.
    """
    scanstr = _infostr('msingle', (settings,) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(args, kwargs, scanstr)
    MiezeScan(settings, [], [], move, multistep, detlist,
              envlist, preset, scaninfo).run()


@usercommand
def mmanualscan(settings, *args, **kwargs):
    """MIEZE scan that works just like `manualscan`."""
    if getattr(session, '_manualscan', None):
        raise UsageError('cannot start manual scan within manual scan')
    return _MiezeManualScan(settings, args, kwargs)
