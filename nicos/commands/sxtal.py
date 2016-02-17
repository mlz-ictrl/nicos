#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2016 by the NICOS contributors (see AUTHORS)
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
#   pedersen
#
# *****************************************************************************

"""
SXtal commands
"""
from nicos import session
# currently not used (otherwise loading in demo fails...
# from nicos.core import ConfigurationError
# from nicos.devices.sxtal.instrument import SXTal
# if not isinstance(session.instrument, SXTal):
#     raise ConfigurationError('Using the single crystal commands is only possible '
#                              'on SXTAL-derived instruments.')

from nicos.commands import usercommand, helparglist
from nicos.core.scan import Scan
class HKLScan(Scan):
    def __init__(self, devices, startpositions, endpositions=None,
                 firstmoves=None, multistep=None, detlist=None, envlist=None,
                 preset=None, scaninfo=None, subscan=False):
        Scan.__init__(self, devices, startpositions, endpositions,
                      firstmoves, multistep, detlist, envlist,
                      preset, scaninfo, subscan)
    def aquire(self, point, preset):
        _scanfuncs[scanmode](point.target)

class CScan(Scan):
  def __init__(self, dev, center, steps, numperside):
        def mkpos(centers, steps, numperside, **kwargs):
        return [[center + (i-numperside)*step for (center, step)
                 in zip(centers, steps)] for i in range(2*numperside+1)]
    values = mkpos(center, steps, numperside)
    scanstr = _infostr('cscan', (dev,) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(restargs, kwargs, scanstr)
    return Scan(devs, values, move, multistep, detlist, envlist, preset,
         scaninfo, subscan=kwargs.get('subscan', False)).run()

@usercommand
@helparglist('dmin, dmax, [scanmode]')
def ScanDataset(dmin, dmax, scanmode=None):
    i = session.instrument
    if scanmode is None:
        scanmode = i.scanmode
    ds = session.experiment.sample.cell.dataset(dmin, dmax)
    HKLScan(i, ds)


@usercommand
@helparglist('hkl')
def ScanOmega(hkl):
    i = session.instrument
    width = i.getScanWidthFor(hkl)
    sps = i.scansteps
    sw = width / sps
    op = i._attached_omega.read(0)
    return CScan(i._attached_omega, op, sw, sps / 2, subscan=True).run()


@usercommand
@helparglist('hkl')
def ScanT2T(hkl):
    i = session.instrument
    width = i.getScanWidthFor(hkl)
    sps = i.scansteps
    sw = width / sps
    i.maw(hkl)
    op = i._attached_omega.read(0)
    tp = i._attached_ttheta.read(0)
    return CScan((i._attached_omega, i._attached_ttheta), (op, tp), (sw, 2 * sw),
                  sps / 2, subscan=True).run()

_scanfuncs = {'omega': ScanOmega,
              't2t': ScanT2T,
              }
