#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
"""
A set of commands special for single crystal diffraction
"""

import os
from os import path

import numpy as np

from nicos import session
from nicos.commands import helparglist, parallel_safe, usercommand
from nicos.commands.analyze import COLHELP, _getData, findpeaks
from nicos.commands.measure import _count
from nicos.commands.scan import cscan, scan
from nicos.core import FINAL, NicosError, Scan
from nicos.core.errors import ConfigurationError
from nicos.core.utils import multiWait
from nicos.devices.generic.detector import DummyDetector
from nicos.devices.sxtal.xtal.sxtalcell import SXTalCell

from nicos_sinq.sxtal.cell import calculateBMatrix
from nicos_sinq.sxtal.instrument import SXTalBase, TASSXTal
from nicos_sinq.sxtal.sample import SXTalSample
from nicos_sinq.sxtal.singlexlib import calcTheta
from nicos_sinq.sxtal.tasublib import KToEnergy, makeAuxReflection
from nicos_sinq.sxtal.util import window_integrate


def getSampleInst():
    """
    helper function to check for applicability of single
    crystal functions.
    """
    sample = session.experiment.sample
    if not isinstance(sample, SXTalSample):
        session.log.error('Sample is not a SXTalSample')
        return None, None
    inst = session.instrument
    if not isinstance(inst, SXTalBase):
        session.log.error('NOT a single crystal experiment')
        return None, None
    return sample, inst


def _auxfilename(filename):
    fn = filename
    if not path.isabs(fn):
        fn = path.normpath(path.join(session.experiment.scriptpath, fn))
    base, ext = os.path.splitext(fn)
    if not ext or ext == '.py':
        return base + '.dat'
    return fn


@usercommand
@helparglist('reciprocal lattice coordinates, angles, '
             'auxiliary information, reflection list')
def AddRef(hkl=None, angles=None, aux=None, reflist=None):
    """
    This commands appends a reflection to a reflection list. If the
    reflist parameter is omitted, the default reflection list is used.
    If both hkl and angles are None, then the current position of the
    instrument is stored in the reflection list. In any other case a
    reflection is entered with the missing information set to defaults.
    """
    def add_current(inst, hkl, rfl, aux):
        angles = inst._readPos()
        rfl.append(hkl, angles, aux)

    def add_current_tas(inst, hkl, rfl):
        angles = inst._readPos()
        aux = KToEnergy(angles[0]), KToEnergy(angles[1])
        angles = angles[2:]
        rfl.append(hkl, angles, aux)

    sample, inst = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    if not hkl and not angles:
        hkl = inst.read(0)
        if isinstance(inst, TASSXTal):
            return add_current_tas(inst, hkl, rfl)
        else:
            return add_current(inst, hkl, rfl, aux)
    if hkl and not angles:
        if isinstance(inst, TASSXTal):
            return add_current_tas(inst, hkl, rfl)
        else:
            return add_current(inst, hkl, rfl, aux)
    rfl.append(hkl, angles, aux)


@usercommand
def DelRef(idx, reflist=None):
    """
    Deletes the reflection idx from the reflection list
    """
    sample, _ = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    rfl.delete(idx)


@usercommand
@parallel_safe
@helparglist('Optional reflection list to list, '
             'if None list the default reflection list')
def ListRef(reflist=None):
    sample, _ = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    header = '%4s' % '#'
    for v in rfl.column_headers[0]:
        header += '%8s' % v
    header += ' '
    for v in rfl.column_headers[1]:
        header += '%8s' % v
    if len(rfl.column_headers[2]) > 0:
        aux = True
        for v in rfl.column_headers[2]:
            header += '%8s' % v
    else:
        aux = False
    session.log.info(header)
    refiter = rfl.generate(0)
    r = next(refiter)
    count = 0
    while r:
        data = '%4d' % count
        for q in r[0]:
            data += '%8.4f' % q
        data += ' '
        for a in r[1]:
            data += '%8.3f' % a
        if aux:
            for v in r[2]:
                data += '%8.3f' % v
        session.log.info(data)
        count += 1
        r = next(refiter)
    session.log.info('--- The End ---')


@usercommand
@helparglist('index of reflection to modify, new reciprocal lattice '
             'coordinates, new angles, new auxiliary data, '
             'reflection list to operate upon')
def SetRef(idx, hkl=None, angles=None, aux=None, reflist=None):
    """
    Modifies the entry for the reflection with the ID idx in reflection list
    reflist
    The values given are modified, the rest uses the existing values
    """
    sample, _ = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    rfl.modify_reflection(idx, hkl, angles, aux)


@usercommand
def ClearRef(reflist=None):
    """
    Clears a reflection list
    """
    sample, _ = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    rfl.clear()


@usercommand
@helparglist('A tuple of (h, k, l) for the auxiliary reflection and the '
             'index of the reference reflection, Optionally the name of '
             'the reflection list to work on')
def AddAuxRef(hkl, idx, reflist=None):
    """
    Add an auxiliary reflection from energies and B matrix.
    Works only for TAS. A3, SGU, SGL will be invalid
    """
    sample, inst = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    if not isinstance(inst, TASSXTal):
        session.log.error('This command does only work for TAS')
        return
    r1 = rfl.get_reflection(idx)
    calcr = inst._rfl_to_reflection(r1)
    cell = sample.getCell()
    B = calculateBMatrix(cell)
    try:
        r2 = makeAuxReflection(B, calcr, inst.scattering_sense, hkl)
        angles = r2.angles.a3, r2.angles.sample_two_theta, 0, 0
        aux = KToEnergy(r2.qe.ki), KToEnergy(r2.qe.kf)
        en = aux[0] - aux[1]
        hl = list(hkl)
        hl.append(en)
        rfl.append(tuple(hl), angles, aux)
    except RuntimeError as e:
        session.log.error(e)
        return


@usercommand
@parallel_safe
@helparglist('Miller indices to calculate angles for')
def CalcAng(hkl):
    """
    Calculate the setting angles for the reflection
    with the miller indices given. Does NOT move the
    diffractometer
    Example: CalcAng((1,1,1))
    """
    sample, inst = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList()
    poslist = inst._extractPos(inst._calcPos(hkl))
    header = ''
    for v in rfl.column_headers[1]:
        header += '%8s' % v
    session.log.info(header)
    data = ''
    for ang in poslist:
        data += '%8.3f' % ang[1]
    session.log.info(data)
    ok, why = inst.isAllowed(hkl)
    if ok:
        session.log.info('Reflection is OK')
    else:
        session.log.info('Reflection outside of limits %s', why)


@usercommand
@parallel_safe
@helparglist('tuple of setting angles, when None, '
             'read current instrument position')
def CalcPos(angles):
    """
    Calculate the reciprocal space coordinates for the angles given
    Example: CalcPos((13.668, 6.834, 18.9, 125.6))
    """
    sample, inst = getSampleInst()
    if not sample:
        return
    hkl = inst._reverse_calpos(angles)
    session.log.info('       H       K       L')
    session.log.info('%8.3f%8.3f%8.3f', hkl[0], hkl[1], hkl[2])


@usercommand
@parallel_safe
def ShowAng():
    """
    Shows the position of all diffractometer motors
    """
    sample, inst = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList()
    pos = inst._readPos()
    posstr = '('
    for p in pos:
        posstr += '%8.3f,' % p
    posstr = posstr[0:-1] + ')'
    session.log.info('%s = %s', str(rfl.column_headers[1]),
                     posstr)


@usercommand
@helparglist('device, step width, '
             'counter to optimise against, maxsteps, preset')
def Max(dev, step, counter=None, maxpts=None, **preset):
    """
    Search the maximum of a peak by moving dev. The algorithm used has
    been taken from the program difrac by P. White and E. Gabe

    The data structure is an array of maxpts elements. We start in the
    middle.

    We first step to the left until we find a point where the counts are
    half of the maximum. If we do not find the peak there we go right
    and do the same. If we cannot find the peak then, we give up.
    Else we calculate the peak as the meridian between left and right
    half maximum.
    """
    def findPeak(left, right):
        # Calculate median
        area = 0
        oidx = 0
        for idx in range(left, right):
            area += (positions[idx+1] - positions[idx]) * \
                    (counts[idx+1] + counts[idx]) * .25
        s = 0
        for idx in range(left, right):
            s += (positions[idx+1] - positions[idx]) * \
                 (counts[idx+1] + counts[idx]) * .5
            oidx = idx
            if s > area:
                break
        s -= .5 * (positions[oidx+1] - positions[oidx]) * \
            (counts[oidx+1] + counts[oidx])
        da = area - s
        if counts[oidx+1] == counts[oidx]:
            center = positions[oidx] + da/counts[oidx]
        else:
            s = (counts[oidx+1] - counts[oidx]) / \
                (positions[oidx+1] - positions[oidx])
            if (counts[oidx]**2 + 2. * s * da) < 0:
                session.log.error('Error calculating peak median')
                return False
            disc = np.sqrt(counts[oidx]**2 + 2.*s*da)
            center = positions[oidx] + (disc - counts[oidx])/s
        for idx in range(left, right+1):
            if positions[idx] <= center < positions[idx+1]:
                peakmax = counts[idx]
                break
        dev.start(center)
        multiWait([dev])
        session.log.info('Found peak at %f, counts = %ld', center, peakmax)
        return True

    inst = session.instrument
    if not isinstance(inst, SXTalBase):
        session.log.error('NOT a single crystal experiment')
        return False
    if not maxpts:
        maxpts = inst.center_maxpts
    if not counter:
        counter = inst.center_counter
    half_point = int(maxpts/2)
    try:
        countdev = session.getDevice(counter)
    except ConfigurationError:
        session.log.error('%s not found, cannot maximize against is', counter)
        return False
    preset['temporary'] = True
    counts = np.zeros((maxpts,), dtype='int32')
    positions = np.zeros((maxpts,), dtype='float32')
    positions[half_point] = dev.read()
    _count(*(), **preset)
    max_count = countdev.read()[0]
    max_idx = half_point
    counts[half_point] = max_count
    idx = half_point - 1
    left_idx = -1
    right_idx = maxpts + 10

    # Search left first
    while idx >= 0:
        i = half_point - idx
        target = positions[half_point] - i * step
        dev.start(target)
        multiWait([dev])
        session.log.info('%s = %f', dev.name, dev.read())
        _count(*(), **preset)
        count = countdev.read()[0]
        counts[idx] = count
        positions[idx] = dev.read()
        if count > max_count:
            max_count = count
            max_idx = idx
        elif count < max_count/2.:
            left_idx = idx
            break
        idx -= 1
    # Test: peak in left half
    if counts[half_point] < max_count / 2.:
        right_idx = max_idx
        while counts[right_idx] > max_count/2.:
            right_idx += 1
        return findPeak(left_idx, right_idx)

    # Search to the right
    idx = half_point + 1
    while idx < maxpts:
        i = idx - half_point
        target = positions[half_point] + i * step
        dev.start(target)
        multiWait([dev])
        session.log.info('%s = %f', dev.name, dev.read())
        _count(*(), **preset)
        count = countdev.read()[0]
        counts[idx] = count
        positions[idx] = dev.read()
        if count > max_count:
            max_count = count
            max_idx = idx
        elif count < max_count/2.:
            right_idx = idx
            break
        idx += 1
        # Test for peak limit not found
    if idx == maxpts and count > max_count/2.:
        session.log.error('Peak out of range')
        return False
    # Test for peak in right half
    if counts[half_point] < max_count / 2. and left_idx < 0:
        left_idx = max_idx
    while counts[left_idx] > max_count / 2.:
        left_idx -= 1
    if left_idx > 0 and right_idx < maxpts:
        return findPeak(left_idx, right_idx)
    session.log.error('Peak out of range')
    return False


def go_reflection(r, devs):
    use_angles = False
    for a in r[1]:
        if abs(a) > .1:
            use_angles = True
            break
    if use_angles:
        for dev, ang in zip(devs, r[1]):
            dev.start(ang)
        multiWait(devs)
    else:
        inst = session.instrument
        inst.start(r[0])
        multiWait([inst])


def inner_center(r, **preset):
    inst = session.instrument
    motors = inst.get_motors()
    steps = inst.center_steps
    go_reflection(r, motors)
    startang = [m.read(0) for m in motors]
    for dev, step in zip(motors, steps):
        if not Max(dev, step, **preset):
            return False, tuple(startang)
    newang = [m.read(0) for m in motors]
    return True, tuple(newang)


@usercommand
@helparglist('reflection index, reflist when not default, preset')
def Center(idx, reflist=None, **preset):
    """Center reflection idx in reflist"""
    sample, _ = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    r = rfl.get_reflection(idx)
    ok, newang = inner_center(r, **preset)
    if ok:
        rfl.modify_reflection(idx, None, newang, None)
    else:
        session.log.error('Failed to center reflection %d', idx)


def process_list(reflist, function, **preset):
    """apply function to all reflections in reflist"""
    refiter = reflist.generate(0)
    r = next(refiter)
    while r:
        function(r, **preset)
        r = next(refiter)


def process_center(reflist, **preset):
    refiter = reflist.generate(0)
    idx = 0
    r = next(refiter)
    while r:
        ok, newang = inner_center(r, **preset)
        if ok:
            reflist.modify_reflection(idx, None, newang, None)
        else:
            if len(r[1]) == 4:
                session.log.error('Failed to center reflection at %f %f %f %f',
                                  r[1][0], r[1][1], r[1][2], r[1][3])
            else:
                session.log.error('Failed to center reflection at %f %f %f',
                                  r[1][0], r[1][1], r[1][2])
        r = next(refiter)
        idx += 1


@usercommand
@helparglist('list of reflections to center, count preset')
def CenterList(reflist, **preset):
    """Center a list of reflections"""
    sample, _ = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    process_center(rfl,  **preset)


def write_rfl(r, **preset):
    out = preset['file']
    hkl = r[0]
    out.write('%8.4f %8.4f %8.4f' % hkl)
    ang = r[1]
    for a in ang:
        out.write(' %8.4f' % a)
    ex = r[2]
    for e in ex:
        out.write(' %8.4f' % e)
    out.write('\n')


def write_rafin(r, **preset):
    out = preset['file']
    hkl = r[0]
    out.write('%9.4f %9.4f %9.4f' % hkl)
    ang = r[1]
    for a in ang:
        out.write(' %8.3f' % a)
    out.write('\n')


def write_rafin_header(out, sample, inst):
    out.write('%s, %s\n' % (session.experiment.title, sample.name))
    out.write('2 1 0 0 45 3 4 1 .5 0\n')
    out.write('0 %8.4f\n' % inst.wavelength)
    out.write('0 .0 0 .0 0 .0\n')
    out.write('0 %8.4f 0 %8.4f 0 %8.4f 0 %8.4f 0 %8.4f 0 %8.4f\n' %
              (sample.a, sample.b, sample.c,
               sample.alpha, sample.beta, sample.gamma))


def write_dirax(r, **preset):
    out = preset['file']
    z1 = session.instrument._convertPos(r[1])
    out.write('%f %f %f\n' % (z1[0], z1[1], z1[2]))


@usercommand
def SaveRef(filename, reflist=None, fmt=None):
    """Save a reflection list into filename. Various formats are supported:
    - None: a plane list
    - rafin: a list for UB refinement with rafin
    - dirax: a list for the indexing program dirax
    """
    sample, inst = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    fname = _auxfilename(filename)
    with open(fname, 'w', encoding='utf-8') as out:
        if fmt and fmt == 'rafin':
            write_rafin_header(out, sample, inst)
            process_list(rfl, write_rafin, **{'file': out})
            out.write('\n')
            out.write('-1\n')
        elif fmt and fmt == 'dirax':
            out.write('%f\n' % inst.wavelength)
            process_list(rfl, write_dirax, **{'file': out})
        else:
            process_list(rfl, write_rfl, **{'file': out})
    session.log.info('Wrote reflection list %s to %s', reflist, fname)


@usercommand
def LoadRef(filename, reflist=None):
    """Loads reflections from filename into reflist"""
    sample, _ = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    fname = _auxfilename(filename)
    rfl.clear()
    count = 0
    with open(fname, 'r', encoding='utf-8') as fin:
        for line in fin:
            values = line.split()
            if len(values) < 3:
                session.log.error('%s not in a recognized format', fname)
                return
            hkl = (float(values[0]), float(values[1]), float(values[2]))
            ang = []
            anglen = len(rfl.column_headers[1])
            if len(values) >= 3 + anglen:
                for i in range(anglen):
                    ang.append(float(values[3 + i]))
            else:
                for i in range(anglen):
                    ang.append(0)
            ang = tuple(ang)
            ext = []
            if len(values) >= 3 + anglen + len(rfl.column_headers[2]):
                for i in range(len(rfl.column_headers[2])):
                    ext.append(float(values[3 + anglen + i]))
            else:
                for i in range(len(rfl.column_headers[2])):
                    ext.append(0)
            ext = tuple(ext)
            rfl.append(hkl, ang, ext)
            count += 1
    session.log.info('Loaded %d reflections from %s', count, fname)


@usercommand
def GenerateList(dmin, dmax, reflist=None):
    """Generate reflections between dmin, dmax and store in reflist"""
    sample, inst = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    sxtal = SXTalCell.fromabc(sample.a, sample.b, sample.c,
                              sample.alpha, sample.beta, sample.gamma,
                              sample.bravais, sample.laue)
    raw_list = sxtal.dataset(dmin, dmax)
    raw_as_list = raw_list.tolist()
    rfl.clear()
    count = 0
    for r in raw_as_list:
        hkl = tuple(r)
        if inst.isAllowed(hkl):
            rfl.append(tuple(r), None, None)
            count += 1
    session.log.info('Generated %d reflections', count)


@usercommand
def GenerateSuper(targetlist, vector, srclist=None):
    """Read srclist and create super structure reflections
    using vector and store them in targetlist. Targetlist is
    NOT cleared beforehand in order to allow for multiple
    applications."""
    sample, _ = getSampleInst()
    if not sample:
        return
    src = sample.getRefList(srclist)
    if src is None:
        session.log.error('Reflection list %s not found', srclist)
        return
    target = sample.getRefList(targetlist)
    if target is None:
        session.log.error('Reflection list %s not found', targetlist)
        return
    if len(vector) != 3:
        session.log.error('Need a three component super structure vector')
        return
    count = 0
    srcit = src.generate(0)
    vec = np.array(vector)
    r = next(srcit)
    while r:
        rm = np.array(r[0])
        newr = rm + vec
        count += 1
        target.append(tuple(newr), (), ())
        newr = rm - vec
        if target.find_reflection(newr) < 0:
            target.append(tuple(newr))
            count += 1
        r = next(srcit)
    # Add super structure reflections for 0, 0, 0
    newr = (0, 0, 0) + vec
    target.append(tuple(newr), (), ())
    count += 1
    newr = (0, 0, 0) - vec
    if target.find_reflection(newr) < 0:
        target.append(tuple(newr), (), ())
        count += 1

    session.log.info('%d super structure reflection generated in %s',
                     count, targetlist)


class Intensity(DummyDetector):

    def presetInfo(self):
        vi = []
        for d in session.experiment.detectors:
            vi += d.presetInfo()
        return set(vi)

    def doRead(self, maxage=0):
        return None


class HKLScan(Scan):
    def __init__(self, devices, startpositions, scanmode='omega',
                 endpositions=None, firstmoves=None,
                 multistep=None, detlist=None, envlist=None,
                 scaninfo=None, subscan=False, **preset):
        self._intensity = session.getDevice('intensity')
        detlist = [self._intensity]
        Scan.__init__(self, devices, startpositions, endpositions,
                      firstmoves, multistep, detlist, envlist,
                      preset, scaninfo, subscan)
        self.scanmode = scanmode

    def endScan(self):
        # This is here for debugging: see datasink.py:152ff
        Scan.endScan(self)

    def acquire(self, point, preset):
        _scanfuncs[self.scanmode](point.target[0], subscan=True,
                                  **self._preset)
        subscan = self.dataset.subsets[-1].subsets[-1]
        index = [i for (i, v) in enumerate(subscan.detvalueinfo)
                 if v.name == session.instrument.center_counter][0]
        vals = [x[index] for x in subscan.detvaluelists]
        if vals:
            _, _, intensity,  _ = window_integrate(vals)
            session.experiment.data.putResults(FINAL,
                                               {'intensity': [intensity]})


@usercommand
@helparglist('hkl')
def ScanOmega(hkl, subscan=False, **preset):
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument device is not a SXTAL device')
    width = instr.getScanWidthFor(hkl)
    sps = instr.scansteps
    sw = width / sps
    op = instr._attached_omega.read(0)
    cscan(instr._attached_omega, op, sw, sps // 2, instr,
          subscan=subscan, **preset)


@usercommand
@helparglist('hkl')
def ScanT2T(hkl, subscan=False, **preset):
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
          [sw, 2 * sw], sps // 2, instr, subscan=subscan, **preset)


_scanfuncs = {
    'omega': ScanOmega,
    't2t': ScanT2T,
}


@usercommand
def Measure(scanmode=None, skip=0, reflist=None, **preset):
    """Measure a reflection list"""
    sample, inst = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    rfliter = rfl.generate(skip)
    r = next(rfliter)
    pos = []
    while r:
        pos.append([r[0]])
        r = next(rfliter)
    if scanmode is None:
        scanmode = inst.scanmode
    inst.ccl_file = True
    HKLScan([inst], pos, scanmode=scanmode, **preset).run()
    inst.ccl_file = False


@usercommand
def IndexTH(idx, reflist=None, hkllim=10):
    """Suggests possible indices based on the 2theta of the reflection"""
    sample, inst = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    r = rfl.get_reflection(idx)
    if not r:
        session.log.error('Reflection %d not found in reflection list',
                          idx)
        return
    z1 = inst._convertPos(r[1])
    _, theta = calcTheta(inst.wavelength, z1)
    rfl_tth = 2. * np.rad2deg(np.arcsin(theta))
    result = []
    for h in range(-hkllim, hkllim):
        for k in range(-hkllim, hkllim):
            for ql in range(-hkllim, hkllim):
                z1 = inst._calcPos((h, k, ql))
                d, theta = calcTheta(inst.wavelength, z1)
                if d == 0:
                    continue
                hkl_tth = 2. * np.rad2deg(np.arcsin(theta))
                if rfl_tth - .2 < hkl_tth < rfl_tth + .2:
                    result.append((h, k, ql, hkl_tth))
    session.log.info('Suggested indices for reflection %d, two_theta= %8.4f',
                     idx, rfl_tth)
    for res in result:
        session.log.info('(%d, %d, %d) tth = %8.4f versus %8.4f',
                         res[0], res[1], res[2], res[3], rfl_tth)


@usercommand
@helparglist('[[xcol, ]ycol]')
def integrate(*columns):
    """Integrate the intensity of the peak"""
    _, ys = _getData(columns)[:2]
    ok, reason, intensity, stddev = window_integrate(list(ys))
    if ok:
        session.log.info(' I = %f, sigma = %f', intensity, stddev)
    else:
        session.log.error('Peak integration error: %s', reason)


integrate.__doc__ += COLHELP.replace('func(', 'integrate(')


@usercommand
def CalcUB(idx1, idx2, replace=False, reflist=None):
    """Calculate a UB matrix from the cell and two reflections
    idx1 and idx2 in reflist. Replace the current UB matrix when
    replace is True"""
    sample, inst = getSampleInst()
    if not sample:
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    r1 = rfl.get_reflection(idx1)
    r2 = rfl.get_reflection(idx2)
    if not r1 or not r2:
        session.log.error('Reflections not found')
        return
    newub = inst.calc_ub(sample.getCell(), r1, r2)
    session.log.info('New UB:\n %s', str(newub))
    if replace:
        sample.ubmatrix = list(newub.flatten())
        inst.orienting_reflections = (idx1, idx2)


@usercommand
@helparglist('key can be stt, chi, phi, other parameters define limits '
             'and step width for search')
def SearchPar(key, minval, maxval, step):
    """Configures the peak search parameters """
    _, inst = getSampleInst()
    if not hasattr(inst, 'searchpars'):
        session.log.error('%s does not support peak search',
                          inst.name)
        return
    sp = dict(inst.searchpars)
    sp[key] = (minval, maxval, step)
    inst.searchpars = sp


@usercommand
@parallel_safe
def ShowSearchPar():
    """Show the peak search parameters"""
    _, inst = getSampleInst()
    if not hasattr(inst, 'searchpars'):
        session.log.error('%s does not support peak search',
                          inst.name)
        return
    txt = '%8s%9s%9s%9s\n' % ('Dev', 'Min', 'Max', 'Step')
    for key, val in inst.searchpars.items():
        txt += '%8s %8.3f %8.3f %8.3f\n' % (key, val[0], val[1], val[2])
    session.log.info(txt)


def test_threshold(xcolumn, ycolumn, pos, threshold):
    """Test for minimum peak count"""
    xs, ys = _getData([xcolumn, ycolumn])[:2]
    for idx in range(len(xs)-1):
        if xs[idx] <= pos < xs[idx+1]:
            break
    if ys[idx] > threshold:
        return True
    return False


def test_proximity(rfl, ang):
    """Test if this close in chi and phi to another
    reflection."""
    rit = rfl.generate(0)
    r = next(rit)
    while r:
        if abs(r[1][2] - ang[2]) < 15 and abs(r[1][3]-ang[3]) < 15:
            return True
        r = next(rit)
    return False


@usercommand
def PeakSearch(reflist=None, threshold=100, **preset):
    sample, inst = getSampleInst()
    if not hasattr(inst, 'searchpars'):
        session.log.error('%s does not support peak search',
                          inst.name)
        return
    rfl = sample.getRefList(reflist)
    if rfl is None:
        session.log.error('Reflection list %s not found', reflist)
        return
    mots = inst.get_motors()
    dstt = session.getDevice(mots[0])
    dom = session.getDevice(mots[1])
    dchi = session.getDevice(mots[2])
    dphi = session.getDevice(mots[3])
    mots = [dstt, dom, dchi, dphi]
    sttpars = inst.searchpars['stt']
    chipars = inst.searchpars['chi']
    phipars = inst.searchpars['phi']
    nphi = (phipars[1] - phipars[0])/phipars[2]
    for stt in np.arange(sttpars[0], sttpars[1], sttpars[2]):
        for chi in np.arange(chipars[0], chipars[1], chipars[2]):
            dstt.start(stt)
            dstt.start(stt / 2.)
            dchi.start(chi)
            multiWait([dstt, dom, dchi])
            session.log.info('Searching at stt = %f, chi = %f', stt, chi)
            scan(dphi, phipars[0], phipars[2], int(nphi), **preset)
            peaks = findpeaks(mots[3].name, inst.center_counter, npoints=4)
            if peaks:
                session.log.info('%d candidate peaks found in phi scan',
                                 len(peaks))
                for p in peaks:
                    dphi.maw(p)
                    ang = [m.read(0) for m in mots]
                    r = ((0, 0, 0), tuple(ang), ())
                    if not test_threshold(dphi.name, inst.center_counter,
                                          p, threshold):
                        session.log.info('Peak at %f below threshold %f',
                                         p, threshold)
                        continue
                    if test_proximity(rfl, ang):
                        session.log.info('Peak at %f failed proximity test',
                                         p)
                        continue
                    session.log.info('Centering reflection at phi = %f', p)
                    ok, maxang = inner_center(r, **preset)
                    if ok:
                        rfl.append(None, tuple(maxang), None)
                    else:
                        session.log.warning('Failed centering at phi = %f', p)
