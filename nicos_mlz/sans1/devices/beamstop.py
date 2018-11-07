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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Beamstop handling for SANS1"""

from __future__ import absolute_import, division, print_function

import numpy as np

from nicos.core import Attach, Moveable, Override, Param, PositionError, \
    UsageError, dictof, limits, oneof, requires, status
from nicos.devices.generic import Axis
from nicos.devices.generic.sequence import SeqCall, SequencerMixin, tupleof
from nicos.devices.tango import Sensor
from nicos.pycompat import iteritems, reraise


class FunnySensor(Sensor):
    """Sensor which sometimes returns senseless values"""
    parameters = {
        'limits': Param('range of sensible values', type=limits, settable=True),
    }

    def doRead(self, maxage=0):
        for _ in range(10):
            # try to filter out 'half-broken' values
            value = np.median([Sensor.doRead(self, maxage) for _ in range(3)])
            # avoid fully broken values
            if self.limits[0] <= value <= self.limits[1]:
                return value
            # at least warn (every retry!)
            self.log.warning('Sensor value %s outside sensible range [%s..%s]' %
                             (value, self.limits[0], self.limits[1]))
        # 10 times no good value -> error
        raise PositionError('Sensor value %s outside sensible range [%s..%s]' %
                            (value, self.limits[0], self.limits[1]))


class BeamStopAxis(Axis):
    """special Axis, which alwas has an offset of 0
    """
    parameter_overrides = {
        'fixed': Override(type=oneof(''), default=''),
        'offset': Override(type=oneof(0.0), default=0.0),
        'lowlevel': Override(default=True),
        'maxtries': Override(default=1000, settable=False),
    }

    def doInit(self, mode):
        Axis.doInit(self, mode)
        if self.maxtries < 1000:
            self._setROParam('maxtries', 1000)
        self._setROParam('userlimits', self.abslimits)

    def doReadOffset(self):
        return 0.

    def doWriteOffset(self, value):
        return 0.

    def doReadUserlimits(self):
        return Axis.doReadAbslimits(self)


class BeamStop(SequencerMixin, Moveable):
    """handles the delicate beamstop

    This device represents the beamstops position as (x,y) tuple

    It also allows to change the shape of the beamstop via an parameter change.

    the beamstop may be freely moved within some limits.
    It also is allowed to exceed these limits at predefined paths to
    change the selected beamstop.
    Between changes, the beamstop may travel along X if it is at a predfiend Y.

    ASCII-art:
    +++++++++++++++++++++++++++++
    +                           +
    +    free move area         +
    +  (userlimits of xaxis     +
    +    + yaxis )              +
    +                           +
    +++++ +++++ +++++ +++++ +++++  <- slots for different shapes
    +++++ +++++ +++++ +++++ +++++
    + travel while shape change +
    +++++++++++++++++++++++++++++
    """

    parameters = {
        'slots':    Param('Mapping of shape to HW-X-value', userparam=False,
                          type=dictof(str, float), mandatory=True),
        'ypassage': Param('HW-Y-value of the passage below the shapes',
                          type=float, mandatory=True, userparam=False),
        'shape':    Param('Currently used shape', type=str, default='unknown',
                          settable=True),
        'offsetxy': Param('Offset of our logical coordinates to the HW coords',
                          type=tupleof(float, float), default=(0., 0.),
                          settable=True),
        'xlimits':  Param('HW-limits for free movement of X', type=limits,
                          mandatory=True, userparam=False),
        'ylimits':  Param('HW-limits for free movement of Y', type=limits,
                          mandatory=True, userparam=False),
    }
    attached_devices = {
        'xaxis': Attach('Axis for the X-movement', BeamStopAxis),
        'yaxis': Attach('Axis for the Y-movement', BeamStopAxis),
    }
    valuetype = tupleof(float, float)
    _honor_stop = True

    def doInit(self, mode):
        self.parameters['shape'].type = oneof(*self.slots)

    def doIsAllowed(self, target):
        target = [target[0] + self.offsetxy[0], target[1] + self.offsetxy[1]]
        # checking for the 'free to move' area
        if self.status()[0] == status.BUSY:
            return False, 'Beamstop busy!'

        # special case: stuck while changing.
        # allow pure horizontal movement in a corridor around ypassage
        # and pure vertical movements if x is near a slot
        xpos = self._attached_xaxis.read()
        ypos = self._attached_yaxis.read()
        xlimits = self.xlimits
        ylimits = self.ylimits
        xprec = self._attached_xaxis.precision
        yprec = self._attached_yaxis.precision
        if ypos < min(ylimits):
            if abs(ypos - self.ypassage) < abs(min(self._attached_yaxis.abslimits) - self.ypassage):
                if abs(target[1] - ypos) <= yprec:
                    return True, 'pure horizontal movement allowed'
            else:
                # purely vertical movement if around a slot
                for slot, slotx in iteritems(self.slots):
                    if abs(xpos - slotx) <= xprec:
                        # at slot 'slot' allow vertical movement
                        if abs(target[0] - xpos) <= xprec:
                            if target[1] >= min(ylimits):
                                # self._setROParam('shape', slot)
                                return True, 'vertical movement in slot ' + slot
        # check for free-move limits
        if not (xlimits[0] <= target[0] <= xlimits[1]):
            return False, 'requested X-position %s outside allowed value, ' \
                          'please move it manually into %s..%s' % (
                              target[0], xlimits[0], xlimits[1])
        if not (ylimits[0] <= target[1] <= ylimits[1]):
            return False, 'requested Y-position %s outside allowed value, ' \
                          'please move it manually into %s..%s' % (
                              target[1], ylimits[0], ylimits[1])

        return True, ''

    def doRead(self, maxage=0):
        return (self._attached_xaxis.read(maxage) - self.offsetxy[0],
                self._attached_yaxis.read(maxage) - self.offsetxy[1])

    def doStart(self, target):
        target = [target[0] + self.offsetxy[0], target[1] + self.offsetxy[1]]
        self._attached_xaxis.start(target[0])
        self._attached_yaxis.start(target[1])

    #@requires(level='admin')
    @requires()
    def doWriteShape(self, target):
        if self._seq_is_running():
            raise UsageError('can not change shape while Busy')
        if not self.shape in self.slots:
            raise UsageError('currently used shape unknown, '
                             '(Call instrument scientist!)')
        if not target in self.slots:
            raise UsageError('unknown shape, use one of %s' %
                             ', '.join([repr(s) for s in self.slots]))
        self._startSequence(self._generateSequence(target))
        # important!
        # shape will be changed by the sequence, so we force the old value here
        return self.shape

    def _generateSequence(self, target):
        seq = []

        startpos = [self._attached_xaxis.read(),
                    self._attached_yaxis.read()]
        lowest_y_pos = min(self.ylimits)

        if startpos[1] < lowest_y_pos:
            raise UsageError('illegal start position for changing shape, '
                             'please call instrument scientist!')

        # construct desired sequence: first move above slot of current shape
        seq.append([SeqCall(Axis.start, self._attached_xaxis,
                            self.slots[self.shape]),
                    SeqCall(Axis.start, self._attached_yaxis, lowest_y_pos)])
        seq.append([SeqCall(self._attached_xaxis.wait),
                    SeqCall(self._attached_yaxis.wait)])
        # move down to ypassage to put shape back to slot/shapeholder
        seq.append(SeqCall(Axis.start, self._attached_yaxis, self.ypassage))
        seq.append(SeqCall(self._attached_yaxis.wait))
        # adjust self._shape
        seq.append(SeqCall(self._setROParam, 'shape', 'none'))
        # move x to slot of new shape
        seq.append(
            SeqCall(Axis.start, self._attached_xaxis, self.slots[target]))
        seq.append(SeqCall(self._attached_xaxis.wait))
        # move up to lowest yvalue
        seq.append(SeqCall(Axis.start, self._attached_yaxis, lowest_y_pos))
        seq.append(SeqCall(self._attached_yaxis.wait))
        # adjust self._shape
        seq.append(SeqCall(self._setROParam, 'shape', target))
        # move to last xvalue
        seq.append([SeqCall(Axis.start, self._attached_xaxis, startpos[0]),
                    SeqCall(Axis.start, self._attached_yaxis, startpos[1])])
        seq.append([SeqCall(self._attached_xaxis.wait),
                    SeqCall(self._attached_yaxis.wait)])
        return seq

    def _runFailed(self, step, action, exc_info):
        return 1  # single retry

    def _retryFailed(self, step, action, exc_info):
        self._seq_stopflag = True
        self._setROParam('fixed', 'Error during sequence (step %r), needs '
                                  'manual fixing!' % step)
        self._setROParam('fixedby', ('admin', 20))
        reraise(*exc_info)
