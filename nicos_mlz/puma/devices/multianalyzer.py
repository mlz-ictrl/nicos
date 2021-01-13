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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#
# *****************************************************************************
"""PUMA multi analyser class."""

from contextlib import contextmanager

from numpy import sign

from nicos import session
from nicos.core import Attach, HasTimeout, IsController, Override, Param, \
    floatrange, status, tupleof
from nicos.core.constants import SIMULATION
from nicos.core.errors import MoveError, PositionError
from nicos.core.utils import filterExceptions, multiWait
from nicos.devices.abstract import CanReference
from nicos.devices.generic.sequence import BaseSequencer, SeqMethod


class PumaMultiAnalyzer(CanReference, IsController, HasTimeout, BaseSequencer):
    """PUMA multianalyzer device.

    The device combines 11 devices consisting of a rotation and a translation.
    """

    _num_axes = 11

    attached_devices = {
        'translations': Attach('Translation axes of the crystals',
                               CanReference, multiple=_num_axes),
        'rotations': Attach('Rotation axes of the crystals',
                            CanReference, multiple=_num_axes),
    }

    parameters = {
        'distance': Param('',
                          type=float, settable=False, default=0),
        'mosaicity': Param('Mosaicity of the crystals',
                           type=floatrange(0, None), unit='deg',
                           category='general', default=0.4),
        'bladewidth': Param('Width of the analyzer crystals',
                            type=floatrange(0, None), unit='mm',
                            category='general', default=25),
        'planedistance': Param('Distance between the net planes of crystals',
                               type=floatrange(0, None), unit='AA',
                               category='general', default=3.354),
        'raildistance': Param('Distance between the rails of the crystals',
                              type=floatrange(0, None), default=20,
                              unit='mm', category='general'),
    }

    parameter_overrides = {
        'timeout': Override(default=600),
        'unit': Override(mandatory=False, default=''),
        'fmtstr': Override(volatile=True),
    }

    hardware_access = False

    stoprequest = 0

    valuetype = tupleof(*(float for i in range(2 * _num_axes)))

    _allowed_called = False

    def doPreinit(self, mode):
        self._rotation = self._attached_rotations
        self._translation = self._attached_translations

    @contextmanager
    def _allowed(self):
        """Indicator: position checks will done by controller itself.

        If the controller methods ``doStart`` or ``doIsAllowed`` are called the
        ``isAdevTargetAllowed`` must give back always True otherwise a no
        movement of any component can be achieved.
        """
        self._allowed_called = True
        yield
        self._allowed_called = False

    def isAdevTargetAllowed(self, dev, target):
        if not self._allowed_called:
            stat = self.doStatus(0)
            if stat[0] != status.OK:
                return False, '%s: Controller device is busy!' % self
            if dev in self._translation:
                return self._check_translation(self._translation.index(dev),
                                               target)
            return self._check_rotation(self._rotation.index(dev), target)
        return True, ''

    def _check_rotation(self, rindex, target):
        delta = self._translation[rindex + 1].read(0) - \
                self._translation[rindex].read(0) \
                if 0 <= rindex < self._num_axes - 1 else 13
        ll, hl = self._rotlimits(delta)
        self.log.debug('%s, %s, %s', ll, target, hl)
        if not ll <= target <= hl:
            return False, 'neighbour distance: %.3f; cannot move rotation ' \
                'to : %.3f!' % (delta, target)
        return True, ''

    def _check_translation(self, tindex, target):
        cdelta = [13, 13]  # current delta between device and neighour devices
        tdelta = [13, 13]  # delta between devices and neighbours at target

        rot = [None, self._rotation[tindex].read(0), None]
        trans = [None, self._translation[tindex].read(0), None]

        # determine the current and the upcoming deltas between translation
        # device and its neighbouring devices
        if tindex < self._num_axes - 1:
            trans[2] = self._translation[tindex + 1].read(0)
            rot[2] = self._rotation[tindex + 1].read(0)
            cdelta[1] = trans[2] - trans[1]
            tdelta[1] = trans[2] - target
        if tindex > 0:
            trans[0] = self._translation[tindex - 1].read(0)
            rot[0] = self._rotation[tindex - 1].read(0)
            cdelta[0] = trans[0] - trans[1]
            tdelta[0] = trans[0] - target
        for dc, dt, r in zip(cdelta, tdelta, rot[::2]):
            # self.log.info('dc:%s dt:%s t:%s r:%s', dc, dt, t, r)
            # self.log.info('s(dc): %s s(dt): %s', sign(dc), sign(dt))
            if 0 in (sign(dc), sign(dt)) or sign(dc) == sign(dt):
                # No passing of the other translation devices
                # self.log.info('No passing device: %s %s', dc, dt)
                if abs(dt) < abs(dc):
                    # self.log.info('Come closer to other device')
                    if r:
                        ll, hl = self._rotlimits(dt)
                        if not ll <= r <= hl:
                            self.log.info('(%s): %s, %s, %s', target, ll, r,
                                          hl)
                            self.log.info('%r, %r; %r', trans, rot, tdelta)
                            return False, 'neighbour distance: %.3f; cannot ' \
                                'move translation to : %.3f!' % (dt, target)
                # elif -13 < dc < 0 and dt < 0:
                #     # self.log.info('It is critical')
                #     if (r is not None and r < -23.33) or rot[1] < -23.33:
                #         return False, 'Path %s to %s is not free. One of ' \
                #             'the mirrors would hit another one. (%s, %s)' % (
                #                 trans[1], target, r, rot[1])
            else:
                # Passing another translation device
                # self.log.info('Passing device: %s %s', dc, dt)
                # self.log.info('rotations: %s %s', r, rot[1])
                if (r is not None and r < -23.33) or rot[1] < -23.33:
                    return False, 'Path %s to %s is not free. One of the ' \
                        'mirrors would hit another one. (%s, %s)' % (
                            trans[1], target, r, rot[1])
        return True, ''

    def doIsAllowed(self, target):
        """Check if requested targets are within allowed range for devices."""
        with self._allowed():
            why = []
            for i, (ax, t) in enumerate(zip(self._rotation,
                                            target[self._num_axes:])):
                ok, w = ax.isAllowed(t)
                if ok:
                    self.log.debug('requested rotation %2d to %.2f deg '
                                   'allowed', i + 1, t)
                else:
                    why.append('requested rotation %d to %.2f deg out of '
                               'limits: %s' % (i + 1, t, w))
            for i, (ax, t) in enumerate(zip(self._translation,
                                            target[:self._num_axes])):
                ok, w = ax.isAllowed(t)
                if ok:
                    self.log.debug('requested translation %2d to %.2f mm '
                                   'allowed', i + 1, t)
                else:
                    why.append('requested translation %2d to %.2f mm out of '
                               'limits: %s' % (i + 1, t, w))
            for i, rot in enumerate(target[self._num_axes:]):
                ll, hl = self._calc_rotlimits(i, target)
                if not ll <= rot <= hl:
                    why.append('requested rotation %2d to %.2f deg out of '
                               'limits: (%.3f, %3f)' % (i + 1, rot, ll, hl))
            if why:
                self.log.info('target: %s', target)
                return False, '; '.join(why)
            return True, ''

    def valueInfo(self):
        ret = []
        for dev in self._translation + self._rotation:
            ret.extend(dev.valueInfo())
        return tuple(ret)

    def doReadFmtstr(self):
        return ', '.join('%s = %s' % (v.name, v.fmtstr)
                         for v in self.valueInfo())

    def _generateSequence(self, target):
        """Move multidetector to correct scattering angle of multi analyzer.

        It takes account into the different origins of the analyzer blades.
        """
        # check if requested positions already reached within precision
        if self.isAtTarget(target=target):
            self.log.debug('device already at position, nothing to do!')
            return []

        return [
            SeqMethod(self, '_move_translations', target),
            SeqMethod(self, '_move_rotations', target),
        ]

    def _move_translations(self, target):
        # first check for translation
        mvt = self._checkPositionReachedTrans(self.doRead(0), target)
        if mvt:
            self.log.debug('The following translation axes start moving: %r',
                           mvt)
            # check if translation movement is allowed, i.e. if all
            # rotation axis at reference switch
            if not self._checkRefSwitchRotation():
                if not self._refrotation():
                    raise PositionError(self, 'Could not reference rotations')

            self.log.debug('all rotation at refswitch, start translation')
            for i, dev in enumerate(self._translation):
                with self._allowed():
                    dev.move(target[i])
            self._hw_wait(self._translation)

            if self._checkPositionReachedTrans(self.doRead(0), target):
                raise PositionError(self, 'Translation drive not successful')
            self.log.debug('translation movement done')

    def _move_rotations(self, target):
        # Rotation Movement
        mvr = self._checkPositionReachedRot(self.doRead(0), target)
        if mvr:
            self.log.debug('The following rotation axes start moving: %r', mvr)
            for i in mvr:
                ll, hl = self._calc_rotlimits(i, target)
                if not ll <= target[self._num_axes + i] <= hl:
                    self.log.warning('neighbour is to close; cannot move '
                                     'rotation!')
                    continue
                with self._allowed():
                    self._rotation[i].move(target[self._num_axes + i])
            self._hw_wait([self._rotation[i] for i in mvr])
            if self._checkPositionReachedRot(self.doRead(0), target):
                raise PositionError(self, 'Rotation drive not successful: '
                                    '%r' % ['%s' % d for d in mvr])
            self.log.debug('rotation movement done')

    def doReset(self):
        for dev in self._rotation + self._translation:
            dev.reset()

    def doReference(self, *args):
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot reference device, device is '
                                'still moving (at %s)!' % self._seq_status[1])
        with self._allowed():
            self._startSequence([SeqMethod(self, '_checkedRefRot'),
                                 SeqMethod(self, '_checkedRefTrans')])

    def _checkedRefRot(self):
        if not self._refrotation():
            self.log.warning('reference of rotations not successful')

    def _checkedRefTrans(self):
        if not self._reftranslation():
            self.log.warning('reference of translations not successful')

    def _hw_wait(self, devices):
        loops = 0
        final_exc = None
        devlist = devices[:]  # make a 'real' copy of the list
        while devlist:
            loops += 1
            for dev in devlist[:]:
                try:
                    done = dev.doStatus(0)[0]
                except Exception as exc:
                    dev.log.exception('while waiting')
                    final_exc = filterExceptions(exc, final_exc)
                    # remove this device from the waiters - we might still
                    # have its subdevices in the list so that _hw_wait()
                    # should not return until everything is either OK or
                    # ERROR
                    devlist.remove(dev)
                if done == status.BUSY:
                    # we found one busy dev, normally go to next iteration
                    # until this one is done (saves going through the whole
                    # list of devices and doing unnecessary HW communication)
                    if loops % 10:
                        break
                    # every 10 loops, go through everything to get an accurate
                    # display in the action line
                    continue
                devlist.remove(dev)
            if devlist:
                session.delay(self._base_loop_delay)
        if final_exc:
            raise final_exc

    def _reference(self, devlist):
        if self.stoprequest == 0:
            for ax in devlist:
                if not ax.motor.isAtReference():
                    self.log.debug('reference: %s', ax.name)
                    ax.motor.reference()
            multiWait([ax.motor for ax in devlist])

        check = 0
        for ax in devlist:
            if ax.motor.isAtReference():
                check += 1
            else:
                self.log.warning('%s is not at reference: %r %r', ax.name,
                                 ax.motor.refpos, ax.motor.read(0))
        return check == len(devlist)

    def _refrotation(self):
        return self._reference(self._rotation)

    def _reftranslation(self):
        return self._reference(self._translation)

    def doRead(self, maxage=0):
        return [dev.read(maxage) for dev in self._translation + self._rotation]

    def _printPos(self):
        out = []
        for i, dev in enumerate(self._translation):
            out.append('translation %2d: %7.2f %s' % (i, dev.read(), dev.unit))
        for i, dev in enumerate(self._rotation):
            out.append('rotation    %2d: %7.2f %s' % (i, dev.read(), dev.unit))
        self.log.debug('%s', '\n'.join(out))

    def _checkRefSwitchRotation(self, rotation=None):
        if rotation is None:
            tocheck = [r.motor for r in self._rotation]
        else:
            tocheck = [self._rotation[i].motor for i in rotation]
        checked = [m.isAtReference() for m in tocheck]
        for c, d in zip(checked, tocheck):
            self.log.debug('rot switch for %s ok, check: %s', d, c)
        return all(checked)

    def _rotlimits(self, delta):
        rmini = -60.
        if -13 < delta < -11.9:
            rmini = -50 + (delta + 20.) * 3
        elif -11.9 <= delta <= -2.8:
            rmini = -23.3
        elif delta > -2.8:
            rmini = -34.5 - delta * 4
        if rmini < -60:
            rmini = -60.
        return rmini, 1.7  # 1.7 max of the absolute limits of the rotations

    def _calc_rotlimits(self, trans, target):
        delta = target[trans + 1] - target[trans] \
            if 0 <= trans < self._num_axes - 1 else 12
        rmin, rmax = self._rotlimits(delta)
        self.log.debug('calculated rot limits (%d %d): %.1f -> [%.1f, %.1f]',
                       trans + 1, trans, delta, rmin, rmax)
        return rmin, rmax

    def _checkPositionReachedTrans(self, position, target=None):
        if target is None:
            return []
        mv = [i for i, (t, p, trans) in enumerate(
              zip(target[0:self._num_axes], position[0:self._num_axes],
                  self._translation)) if abs(t - p) > trans.precision]
        for i in range(self._num_axes):
            if i in mv:
                self.log.debug('xx%2d translation start moving', i + 1)
            else:
                self.log.debug('xx%2d translation: nothing to do', i + 1)
        return mv

    def _checkPositionReachedRot(self, position, target=None):
        if target is None:
            return []
        mv = [i for i, (t, p, rot) in enumerate(
              zip(target[self._num_axes:2 * self._num_axes],
                  position[self._num_axes:2 * self._num_axes],
                  self._rotation)) if abs(t - p) > rot.precision]
        for i in range(self._num_axes):
            if i in mv:
                self.log.debug('xx%2d rotation start moving', i + 1)
            else:
                self.log.debug('xx%2d rotation: nothing to do', i + 1)
        return mv

    def doIsAtTarget(self, pos, target):
        mvt = self._checkPositionReachedTrans(pos, target)
        mvr = self._checkPositionReachedRot(pos, target)
        return not mvt and not mvr
