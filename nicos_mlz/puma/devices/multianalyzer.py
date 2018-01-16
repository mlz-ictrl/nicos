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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#
# *****************************************************************************
"""PUMA multi analyser class."""

import sys

from nicos import session
from nicos.core import Attach, HasTimeout, Moveable, Override, Param, status, \
    tupleof
from nicos.core.errors import PositionError
from nicos.core.utils import filterExceptions, multiStatus, multiWait

from nicos.devices.abstract import CanReference

from nicos.pycompat import reraise


class PumaMultiAnalyzer(CanReference, HasTimeout, Moveable):
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
                          type=float, settable=False, default=0,),
        'general_reset': Param('',
                               type=int, settable=False, default=0),
        '_status': Param('read only status',
                         type=bool, settable=False, userparam=False,
                         default=False),
    }

    parameter_overrides = {
        'timeout': Override(default=600),
        'unit': Override(mandatory=False, default=''),
        'fmtstr': Override(volatile=True),
    }

    hardware_access = False

    stoprequest = 0

    valuetype = tupleof(*(float for i in range(2 * _num_axes)))

    def doInit(self, mode):
        self._rotation = self._attached_rotations
        self._translation = self._attached_translations
        self._setROParam('_status', False)

    def doIsAllowed(self, target):
        """Check if requested targets are within allowed range for devices."""
        why = []
        for i, (ax, t) in enumerate(zip(self._rotation,
                                        target[self._num_axes:])):
            ok, w = ax.isAllowed(t)
            if ok:
                self.log.debug('requested rotation %2d to %.2f deg allowed',
                               i + 1, t)
            else:
                why.append('requested rotation %d to %.2f deg out of limits: '
                           '%s' % (i + 1, t, w))
        for i, (ax, t) in enumerate(zip(self._translation,
                                        target[:self._num_axes])):
            ok, w = ax.isAllowed(t)
            if ok:
                self.log.debug('requested translation %2d to %.2f mm allowed',
                               i + 1, t)
            else:
                why.append('requested translation %2d to %.2f mm out of '
                           'limits: %s' % (i + 1, t, w))
        for i, rot in enumerate(target[self._num_axes:]):
            l, h = self._calc_rotlimits(i, target)
            if not l <= rot <= h:
                why.append('requested rotation %2d to %.2f deg out of limits: '
                           '(%.3f, %3f)' % (i + 1, rot, l, h))
        if why:
            return False, '; '.join(why)
        return True, ''

    def _calc_rotlimits(self, trans, target):
        if 0 <= trans < 10:
            deltati = target[trans + 1] - target[trans]
            if deltati < -11.9:
                rmini = -50 + (deltati + 20) * 3
            elif -11.9 <= deltati <= -2.8:
                rmini = -23.3
            if deltati > -2.8:
                rmini = -34.5 - deltati * 4
            if (rmini < -60):
                rmini = -60.
        else:
            deltati = -12
            rmini = -60.
        self.log.debug('calculated rot limits (%d %d): %.1f -> [%.1f, %.1f]',
                       trans + 1, trans, deltati, rmini, 0.5)
        return rmini, 0.5

    def doStatus(self, maxage=0):
        if self._status:
            return status.BUSY, 'moving'
        return multiStatus(self._adevs, maxage)

    def valueInfo(self):
        ret = []
        for dev in self._attached_translations + self._attached_rotations:
            ret.extend(dev.valueInfo())
        return tuple(ret)

    def doReadFmtstr(self):
        return ', '.join('%s = %s' % (v.name, v.fmtstr)
                         for v in self.valueInfo())

    def doStart(self, target):
        try:
            self._setROParam('_status', True)
            # check if requested positions already reached within precision
            mvt, mvr = self._checkPositionReached(target)
            if not mvt and not mvr:
                self.log.debug('device already at requested position, nothing '
                               'to do!')
                self._printPos()
                return

            # requested position not equal current position ==>> start checking
            # for allowed movement

            # first check for translation
            if mvt:
                self.log.debug('The following translation axes start moving: '
                               '%r', mvt)
                # check if translation movement is allowed, i.e. if all
                # rotation axis at reference switch
                if not self._checkRefSwitchRotation(range(self._num_axes)):
                    if not self._refrotation():
                        raise PositionError(self, 'Could not reference '
                                            'rotations')

                self.log.debug('all rotation at refswitch, start translation')
                for i, dev in enumerate(self._translation):
                    dev.move(target[i])
                self._hw_wait(self._translation)

                if self._checkPositionReachedTrans(target):
                    raise PositionError(self, 'Axes: %r did not reach target')
                self.log.debug('translation movement done')

            # Rotation Movement
            mvr = self._checkPositionReachedRot(target)
            if mvr:
                self.log.debug('The following rotation axes start moving: %r',
                               mvr)
                for i in mvr:
                    if not self._checkTransNeighbour(i):
                        self.log.warn('neighbour XX distance < %7.3f; cannot '
                                      'move rotation!', self.distance)
                        continue
                    # TODO: check move or maw
                    self._rotation[i].move(target[self._num_axes + i])
                self._hw_wait([self._rotation[i] for i in mvr])
                if self._checkPositionReachedRot(target):
                    raise PositionError(self, 'Rotation drive not successful')
                self.log.debug('rotation movement done')
        finally:
            self._setROParam('_status', False)
            self._printPos()
            self.log.debug('Analyser movement done')

    def doReset(self):
        for dev in self._rotation + self._translation:
            dev.reset()

    def doReference(self, *args):
        check = self._refrotation()
        if not check:
            self.log.warn('reference of rotations not successful')
        check += self._reftranslation()
        if check != 2:
            self.log.warn('reference of translations not succesful')
        else:
            self.log.debug('reset of %s sucessful', self.name)

    def _hw_wait(self, devices):
        loops = 0
        final_exc = None
        devlist = devices[:]  # make a 'real' copy of the list
        while devlist:
            loops += 1
            for dev in devlist[:]:
                try:
                    done = dev.doStatus(0)[0]
                except Exception:
                    dev.log.exception('while waiting')
                    final_exc = filterExceptions(sys.exc_info(), final_exc)
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
            reraise(*final_exc)

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
                self.log.warn('%s is not at reference: %r %r', ax.name,
                              ax.motor.refpos, ax.motor.read(0))
        return check == len(devlist)

    def _refrotation(self):
        return self._reference(self._rotation)

    def _reftranslation(self):
        # TODO: Check if reset is really needed !
        # if self.stoprequest == 0:
        #     for ax in self._translation:
        #         if not ax.motor.isAtReference():
        #             ax.motor.usermin = 0
        #             session.delay(0.5)
        #             ax.motor.usermax = 0
        #             ax.reset()
        #             session.delay(0.5)
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

    def _checkRefSwitchRotation(self, rotation):
        checkrefswitch = 0
        for i in rotation:
            if self._rotation[i].motor.isAtReference():
                checkrefswitch += 1
                self.log.debug('rot switch for %s ok, check: %s',
                               self._rotation[i], checkrefswitch)
        return checkrefswitch == len(rotation)

    # to be checked
    def _checkTransNeighbour(self, trans):
        if not 0 <= trans < self._num_axes:
            self.log.warn('cannot move translation: %d', trans)
            return False

        self.log.debug('checkTransNeigbour: %s %s %s', trans - 1, trans,
                       trans + 1)
        tr0 = self._translation[trans].read()
        if trans == 0:  # No left neighbour
            tr2 = self._translation[trans + 1].read()
            self.log.debug('case 0: neighbour translations:%s %s', tr0, tr2)
            return abs(tr0 - tr2) >= self.distance
        elif trans == 10:  # No right neighbour
            tr1 = self._translation[trans - 1].read()
            self.log.debug('case 10: neighbour translations:%s %s', tr1, tr0)
            return abs(tr0 - tr1) >= self.distance
        else:
            tr1 = self._translation[trans - 1].read()
            tr2 = self._translation[trans + 1].read()
            self.log.debug('neighbour translations:%s %s %s', tr1, tr0, tr2)
            return abs(tr0 - tr1) >= self.distance and \
                abs(tr0 - tr2) >= self.distance

    def _checkPositionReachedTrans(self, position):
        mv = []
        request = self.doRead(0)[0:self._num_axes]

        for i in range(len(self._translation)):
            if abs(position[i] - request[i]) > self._translation[i].precision:
                self.log.debug('xx%2d translation start moving', i + 1)
                mv.append(i)
            else:
                self.log.debug('xx%2d translation: nothing to do', i + 1)
        return mv

    def _checkPositionReachedRot(self, position):
        mv = []
        request = self.doRead(0)[self._num_axes:2 * self._num_axes]

        for i in range(len(self._rotation)):
            if abs(position[i + self._num_axes] - request[i]) > \
               self._rotation[i].precision:
                self.log.debug('xx%2d rotation start moving', i + 1)
                mv.append(i)
            else:
                self.log.debug('xx%2d rotation: nothing to do', i + 1)
        return mv

    def _checkPositionReached(self, position):
        mvt = self._checkPositionReachedTrans(position)
        mvr = self._checkPositionReachedRot(position)
        return [mvt, mvr]
