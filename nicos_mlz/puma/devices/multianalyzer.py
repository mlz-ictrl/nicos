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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#
# *****************************************************************************
"""PUMA multi analyser class."""

from nicos.core import Attach, HasTimeout, Moveable, Override, Param
from nicos.core.errors import PositionError
from nicos.core.utils import multiWait

from nicos.devices.abstract import CanReference


class PumaMultiAnalyzer(CanReference, HasTimeout, Moveable):

    attached_devices = {
        'translations': Attach('Translation axes of the crystals',
                               CanReference, multiple=11),
        'rotations': Attach('Rotation axes of the crystals',
                            CanReference, multiple=11),
    }

    parameters = {
        'distance': Param('',
                          type=float, settable=False, default=0,),
        'general_reset': Param('',
                               type=int, settable=False, default=0),
    }

    parameter_overrides = {
        'timeout': Override(default=600),
        'unit': Override(mandatory=False, default=''),
    }

    hardware_access = False

    stoprequest = 0

    def doInit(self, mode):
        self._rotation = self._attached_rotations
        self._translation = self._attached_translations

    def doIsAllowed(self, target):
        """Check if requested targets are within allowed range for devices."""
        if len(target) != 22:
            return False, 'requested positions not complete: ' \
                          'no. of positions %s instead of 22 ! (%r)' % (
                              len(target), target)

        notallowed = False
        why = []
        for i in range(11):
            ok, _why = self._translation[i].isAllowed(target[i])
            if ok:
                self.log.debug('requested translation %2d to %.2f mm allowed',
                               i + 1, target[i])
            else:
                why.append('requested translation %2d to %.2f mm out of '
                           'limits: %s' % (i + 1, target[i], _why))
                notallowed = True

        for i in range(11, 22):
            ok, _why = self._rotation[i - 11].isAllowed(target[i])
            if ok:
                self.log.debug('requested rotation %2d to %.2f deg allowed',
                               i - 11 + 1, target[i])
            else:
                why.append('requested rotation %d to %.2f deg out of limits: '
                           '%s' % (i - 11 + 1, target[i], _why))
                notallowed = True

        if notallowed:
            return False, '; '.join(why)
        return True, ''

    def doStart(self, target):
        # check if requested positions already reached within precision
        mvt, mvr = self._checkPositionReached(target)
        if not mvt and not mvr:
            self.log.debug('device already at requested position, nothing to '
                           'do!')
            self._printPos()
            return

        # requested position not equal current position ==>> start checking
        # for allowed movement

        # first check for translation
        if mvt:
            self.log.debug('The following translation axes start moving: %r',
                           mvt)
            # check if translation movement is allowed, i.e. if all
            # rotation axis at reference switch
            if not self._checkRefSwitchRotation(range(11)):
                if not self._refrotation():
                    raise PositionError(self, 'Could not reference rotations')

            self.log.debug('all rotation at refswitch, start translation')
            for i, dev in enumerate(self._translation):
                dev.move(target[i])
            multiWait(self._translation)

            if self._checkPositionReachedTrans(target):
                raise PositionError(self, 'Axes: %r did not reach target')
            self.log.debug('translation movement done')

            # else:
            #     # try to reference individual reference switches, then drive
            #     # translation checks if neighbouring translations are far
            #     # enough to reference if yes, drive to reference sucessful
            #     # -> yes -> drive translation
            #     for i in mvt:
            #         self.log.debug('list mvt %d %r, %s, %s, %s, %s',
            #                        len(mvt), mvt, i, i - 1, i + 1, target[i])

            #         for j in range(3):
            #             if 0 in mvt:
            #                 self.log.info('0 in mvt')
            #                 if not self._checkRefSwitchRotation([i]):
            #                     self.log.info('move %s to refswitch',
            #                                   self._rotation[i])
            #                     if self._checkTransNeighbour(i):
            #                         self._rotation[i].reference()
            #                         self._rotation[i].wait()
            #                 if not self._checkRefSwitchRotation([i + 1]):
            #                     self.log.info('move +1 %s to refswitch',
            #                                   self._rotation[i + 1])
            #                     if self._checkTransNeighbour(i + 1):
            #                         self._rotation[i + 1].reference()
            #                         self._rotation[i + 1].wait()
            #                 if self._checkRefSwitchRotation([i, i + 1]):
            #                     self._translation[mvt[i]].maw(target[i])

            #                 if not self._checkPositionReachedTrans(
            #                    target)[0]:
            #                     self.log.debug('translation movement '
            #                                    'done case 3a')
            #                     break
            #             elif 10 in mvt:
            #                 self.log.info('10 in mvt')
            #                 if not self._checkRefSwitchRotation([i]):
            #                     self.log.info('move %s to refswitch',
            #                                   self._rotation[i])
            #                     if self._checkTransNeighbour(i):
            #                         self._rotation[i].reference()
            #                         self._rotation[i].wait()

            #                 if not self._checkRefSwitchRotation([i - 1]):
            #                     self.log.info('move -1 %s to refswitch',
            #                                   self._rotation[i - 1])
            #                     if self._checkTransNeighbour(i - 1):
            #                         self._rotation[i - 1].reference()
            #                         self._rotation[i - 1].wait()
            #                 if self._checkRefSwitchRotation([i, i - 1]):
            #                     self._translation[mvt[i]].maw(target[i])

            #                 if not self._checkPositionReachedTrans(
            #                    target)[0]:
            #                     self.log.debug('translation movement '
            #                                    'done case 3b')
            #                     break
            #             elif self._checkRefSwitchRotation(
            #                     [i, i - 1, i + 1]):
            #                 self._translation[i].maw(target[i])

            #                 if self._checkPositionReachedTrans(
            #                    target)[0] == 0:
            #                     self.log.debug('translation movement '
            #                                    'done case 3c')
            #                     break
            #             elif not self._checkRefSwitchRotation(
            #                     [i, i - 1, i + 1]):
            #                 self.log.info('j: %s check for translation '
            #                               'allowed', j)
            #                 if not self._checkRefSwitchRotation([i]):
            #                     self.log.info('move %s to refswitch',
            #                                   self._rotation[i])
            #                     if self._checkTransNeighbour(i):
            #                         self._rotation[i].reference()
            #                         self._rotation[i].wait()
            #                 if not self._checkRefSwitchRotation([i - 1]):
            #                     self.log.info('move -1 %s to refswitch',
            #                                   self._rotation[i - 1])
            #                     if self._checkTransNeighbour(i - 1):
            #                         self._rotation[i - 1].reference()
            #                         self._rotation[i - 1].wait()
            #                 if not self._checkRefSwitchRotation([i + 1]):
            #                     self.log.info('move +1 %s to refswitch',
            #                                   self._rotation[i + 1])
            #                     if self._checkTransNeighbour(i + 1):
            #                         self._rotation[i + 1].reference()
            #                         self._rotation[i + 1].wait()

            #                 if self._checkRefSwitchRotation(
            #                    [i, i - 1, i + 1]):
            #                     self._translation[i].maw(target[i])

            #                 if not self._checkPositionReachedTrans(
            #                    target)[0]:
            #                     self.log.debug('translation movement '
            #                                    'done case 4')
            #                     break
            #                 else:
            #                     raise PositionError(self, 'Translation '
            #                                         'drive not successful')
            #             else:
            #                 self.log.error('cannot move translation:%s', i)

            #       multiWait(self._translation)

        # Rotation Movement
        mvr = self._checkPositionReachedRot(target)
        if mvr:
            self.log.debug('The following rotation axes start moving: %r', mvr)
            for i in mvr:
                if not self._checkTransNeighbour(i):
                    self.log.warn('neighbour XX distance < %7.3f; cannot move '
                                  'rotation!', self.distance)
                    continue
                # TODO: check move or maw
                self._rotation[i].move(target[i + 11])
            multiWait([self._rotation[i] for i in mvr])
            if self._checkPositionReachedRot(target):
                raise PositionError(self, 'Rotation drive not successful')
            self.log.debug('rotation movement done')
        self._printPos()
        self.log.debug('Analyser movement done')

    def doReset(self):
        for dev in self._rotation + self._translation:
            dev.reset()

    def doReference(self, *args):
        check = 0
        if self._refrotation():
            check += 1
        else:
            self.log.warn('reset of rotation not successful')

        if self._reftranslation():
            check += 1
        else:
            self.log.warn('cannot reset translation')

        if check == 2:
            self.log.info('reset of %s sucessful', self.name)

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

    def doStop(self):
        for dev in self._translation + self._rotation:
            dev.stop()

    def doRead(self, maxage=0):
        return [dev.read() for dev in self._translation + self._rotation]

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
        if not 0 <= trans < 11:
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
        request = self.doRead()[0:11]

        for i in range(len(self._translation)):
            if abs(position[i] - request[i]) > self._translation[i].precision:
                self.log.debug('xx%2d translation start moving', i + 1)
                mv.append(i)
            else:
                self.log.debug('xx%2d translation: nothing to do', i + 1)
        return mv

    def _checkPositionReachedRot(self, position):
        mv = []
        request = self.doRead()[11:22]

        for i in range(len(self._rotation)):
            if abs(position[i + 11] - request[i]) > self._rotation[i].precision:
                self.log.debug('xx%2d rotation start moving', i + 1)
                mv.append(i)
            else:
                self.log.debug('xx%2d rotation: nothing to do', i + 1)
        return mv

    def _checkPositionReached(self, position):
        mvt = self._checkPositionReachedTrans(position)
        mvr = self._checkPositionReachedRot(position)
        return [mvt, mvr]
