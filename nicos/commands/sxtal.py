#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   pedersen
#
# *****************************************************************************

"""
Commands for single-crystal diffraction.
"""

from nicos import session
from nicos.core import Scan, FINAL, NicosError
from nicos.commands import usercommand, helparglist
from nicos.commands.scan import cscan
from nicos.devices.generic.detector import DummyDetector
from nicos.devices.sxtal.instrument import SXTalBase


class Intensity(DummyDetector):
    temporary = True


class HKLScan(Scan):
    def __init__(self, devices, startpositions, scanmode='omega', endpositions=None,
                 firstmoves=None, multistep=None, detlist=None, envlist=None,
                 preset=None, scaninfo=None, subscan=False):
        self._intensity = Intensity('intensity')
        detlist = [self._intensity]
        Scan.__init__(self, devices, startpositions, endpositions,
                      firstmoves, multistep, detlist, envlist,
                      preset, scaninfo, subscan)
        self.scanmode = scanmode

    def acquire(self, point, preset):
        _scanfuncs[self.scanmode](point.target[0],
                                  preset=self._preset['t'], subscan=True)
        subscan = self.dataset.subsets[-1].subsets[-1]
        index = [i for (i, v) in enumerate(subscan.detvalueinfo)
                 if v.type == 'counter'][0]
        vals = [x[index] for x in subscan.detvaluelists]
        if vals:
            session.data.putResults(FINAL, {'intensity': [max(vals)]})


@usercommand
@helparglist('peaklist, [preset], [scanmode]')
def ScanList(peaklist, preset=1., scanmode=None):
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument device is not a SXTAL device')
    if scanmode is None:
        scanmode = instr.scanmode
    if not isinstance(peaklist, list):
        lst = session.experiment.sample.peaklists.get(peaklist)
        if lst is None:
            raise NicosError('no peak list named %s found' % peaklist)
    pos = [[v] for v in peaklist]
    HKLScan([instr], pos, scanmode=scanmode, preset={'t': preset}).run()


@usercommand
@helparglist('dmin, dmax, [preset], [scanmode]')
def ScanDataset(dmin, dmax, preset=1., scanmode=None):
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument device is not a SXTAL device')
    if scanmode is None:
        scanmode = instr.scanmode
    ds = session.experiment.sample.cell.dataset(dmin, dmax)
    pos = [[v] for v in ds.tolist()]
    # session.log.info(pos)
    HKLScan([instr], pos, scanmode=scanmode, preset={'t': preset}).run()


@usercommand
@helparglist('hkl')
def ScanOmega(hkl, preset=1., subscan=False):
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument device is not a SXTAL device')
    width = instr.getScanWidthFor(hkl)
    sps = instr.scansteps
    sw = width / sps
    op = instr._attached_omega.read(0)
    cscan(instr._attached_omega, op, sw, sps / 2, instr,
          preset, subscan=subscan)


@usercommand
@helparglist('hkl')
def ScanT2T(hkl, preset=1., subscan=False):
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument device is not a SXTAL device')
    width = instr.getScanWidthFor(hkl)
    sps = instr.scansteps
    sw = width / sps
    instr.maw(hkl)
    op = instr._attached_omega.read(0)
    tp = instr._attached_ttheta.read(0)
    cscan([instr._attached_omega, instr._attached_ttheta], [op, tp],
          [sw, 2 * sw], sps / 2, instr, preset, subscan=subscan)

_scanfuncs = {
    'omega': ScanOmega,
    't2t': ScanT2T,
}
