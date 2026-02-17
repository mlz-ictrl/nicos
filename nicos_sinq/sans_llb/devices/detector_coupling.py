# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************
from nicos.core import Attach, floatrange, LimitError, Moveable, Param, PositionError
from nicos.devices.generic import BaseSequencer
from nicos.devices.generic.sequence import SeqWait, SequenceItem, SeqNOP
from nicos.core.status import OK, NOTREACHED

class SeqMove(SequenceItem):
    """
    Move the given device to the given target without waiting.
    """

    def __init__(self, dev, target, stoppable=True):
        SequenceItem.__init__(self, dev=dev, target=target, stoppable=stoppable)

    def check(self):
        res = self.dev.isAllowed(self.target)
        if not res[0]:
            raise LimitError(self.dev, res[1])

    def run(self):
        self.dev.start(self.target)

    def isCompleted(self):
        return True

    def __repr__(self):
        return '%s -> %s' % (self.dev.name, self.dev.format(self.target))

    def stop(self):
        if self.stoppable:
            self.dev.stop()

class SeqWaitThreashold(SequenceItem):
    """Wait for the given device to reach certain threshold from either below or above."""

    def __init__(self, dev, pos, from_below=True):
        self.target = pos
        self.from_below = from_below
        SequenceItem.__init__(self, dev=dev)

    def run(self):
        pass

    def isCompleted(self):
        # dont wait on fixed devices
        pos = self.dev.read()
        if (hasattr(self.dev, 'fixed') and self.dev.fixed) or self.dev.isCompleted():
            if ((2*int(self.from_below)-1)*(pos-self.target))>=-0.5:
                return True
            else:
                raise PositionError(f"Device {self.dev.name} is not moving but condition still not met")
        return ((2*int(self.from_below)-1)*(pos-self.target)) >=0

    def __repr__(self):
        return 'wait for %s to cross %s %s' % (self.dev.name, self.target, "from below" if self.from_below else "from above")

    def stop(self):
        self.dev.stop()


class SansLlbCoupledDetectors(BaseSequencer):
    """
    A device used to make a coupled motion of the low- and high-angle detectors.
    Keeps the ratio between both detector distances constant and moves the high-angle
    horizontal position to correspond to keept it in line with the outer edge of the low-anlge detector
    """
    parameters = {
        'low_angle_frame_x': Param('Position of the low-angle detector left edge from beam center [mm]',
                                type=float, default=500.0),
        'low_angle_frame_y': Param('Position of the low-angle detector bottom edge from beam center [mm]',
                                type=float, default=500.0),
        'high_angle_opening_x': Param('Position of the high-angle detector right edge from beam center [mm]',
                                    type=float, default=400.0),
        'high_angle_opening_y': Param('Position of the high-angle detector top edge from beam center [mm]',
                                    type=float, default=400.0),
        'save_distance_z': Param('Distance to keep between two detectors [mm]',
                                    type=float, default=1000.0),
        'low_high_ratio': Param('User settable ratio between detector distances low/high',
                                type=floatrange(1.1, 20.0), default=3.0, settable=True),
        }

    attached_devices = {
        'low_angle_x': Attach('Translation of low-angle detector horizontal', Moveable),
        'low_angle_z': Attach('Translation of low-angle detector along beam axis', Moveable),
        'sample_offset_z': Attach('Offset device to take into account when calculating detector distance',
                                  Moveable),
        'high_angle_x': Attach('Translation of high-angle detector horizontal', Moveable),
        'high_angle_y': Attach('Translation of high-angle detector vertically', Moveable),
        'high_angle_z': Attach('Translation of high-angle detector along beam axis', Moveable),
        }

    def _calc_destinations(self, target=None):
        if target is None:
            target = self._attached_low_angle_z.read()+self._attached_sample_offset_z.read()
        low_x = self._attached_low_angle_x.read()
        # calculate new positions for all moving devices
        # first detector is a factor 1/ratio closer to sample
        target_z = target/self.low_high_ratio
        # bracket target position by motion limits, mostly relevant for short detector distances
        target_z = max(min(target_z, self._attached_high_angle_z.userlimits[1]),
                       self._attached_high_angle_z.userlimits[0])

        # first detector is horizontal/vertical moved to cover the edge of the second detector,
        # which is at x2/z2 = x2/(x/ratio) = tan = x/z
        actual_lhr = target/target_z
        # move x in opposite direction, allowing to expand q-range when off-centered
        target_x = (self.low_angle_frame_x-low_x)/actual_lhr-self.high_angle_opening_x
        target_y = -self.low_angle_frame_y/actual_lhr+self.high_angle_opening_y
        # bracket target positions
        target_x = max(min(target_x, self._attached_high_angle_x.userlimits[1]),
                       self._attached_high_angle_x.userlimits[0])
        target_y = max(min(target_y, self._attached_high_angle_y.userlimits[1]),
                       self._attached_high_angle_y.userlimits[0])
        return target_x, target_y, target_z

    def _generateSequence(self, target):
        """
        Move the low-angle and heigh-angle to keep the user-defined ratio.
        Move in parallel but avoid colision by waiting for other detector to be away from destination position.
        """

        curr_stz = self._attached_sample_offset_z.read()
        curr_low = self._attached_low_angle_z.read()
        target_x, target_y, target_z = self._calc_destinations(target)

        # create the sequence items to be executed
        if abs(target-curr_low-curr_stz)>0.5:
            lowz = SeqMove(self._attached_low_angle_z, target-curr_stz)
        else:
            # don't move low angle detector if at target, prevent HV cycling
            lowz = SeqNOP()
        highz = SeqMove(self._attached_high_angle_z, target_z)

        highx = SeqMove(self._attached_high_angle_x, target_x)
        highy = SeqMove(self._attached_high_angle_y, target_y)

        final_wait = [SeqWait(self._attached_low_angle_z), SeqWait(self._attached_high_angle_z),
                      SeqWait(self._attached_high_angle_x),SeqWait(self._attached_high_angle_y)]

        if target>curr_low:
            # moving detectors backwards; start with low angle z and wait for it to pass high angle z target
            wait1=SeqWaitThreashold(self._attached_low_angle_z, target_z+self.save_distance_z, from_below=True)
            return [lowz, highx, highy, wait1, highz]+final_wait
        else:
            # moving detectors forward; start with high angle z and wait for it to pass low angle z target
            wait1=SeqWaitThreashold(self._attached_high_angle_z, target-self.save_distance_z, from_below=False)
            return [highz, highx, highy, wait1, lowz]+final_wait

    def doRead(self, maxage=0):
        # total sample-detector distance is dtlz + stz
        return self._attached_low_angle_z.read(maxage=maxage)+self._attached_sample_offset_z.read(maxage=maxage)

    def doStatus(self, maxage=0):
        status, text = super().doStatus(maxage=maxage)
        if status!=OK:
            return status, text
        # check if any detector was moved separately from expected targets
        target_x, target_y, target_z = self._calc_destinations()
        text = f'L/H: {self.low_high_ratio}'
        if abs(self._attached_high_angle_x.read()-target_x)>1.0:
            status = NOTREACHED
            text += ' | x off trgt'
        if abs(self._attached_high_angle_y.read()-target_y)>1.0:
            status = NOTREACHED
            text += ' | y off trgt'
        if abs(self._attached_high_angle_z.read()-target_z)>1.0:
            status = NOTREACHED
            text += ' | z off trgt'
        return status, text
