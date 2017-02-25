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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Class for controlling the KWS1 polarizer."""

from nicos.core import Moveable, Param, Override, Attach, SIMULATION, \
    oneof, tupleof, listof, MoveError, ConfigurationError
from nicos.devices.generic import MultiSwitcher
from nicos.devices.generic.sequence import SequencerMixin, SeqDev
from nicos.utils import num_sort

POL_SETTINGS = ['out', 'up', 'down']


class PolSwitcher(SequencerMixin, MultiSwitcher):
    """The turntable that contains the polarizer or neutron guide.

    Changing the table positions has to be done in a certain order, so that
    the final positions of the polarizer or guide are always reproducible.
    """

    parameters = {
        'movepos':  Param('Position (xv, yv, xh, yh) while rotating',
                          type=tupleof(float, float, float, float),
                          default=(5., 5., 5., 5.)),
    }

    parameter_overrides = {
        'fmtstr':     Override(default='%s'),
        'unit':       Override(mandatory=False, default=''),
    }

    def doInit(self, mode):
        MultiSwitcher.doInit(self, mode)
        if len(self._attached_moveables) != 5:
            raise ConfigurationError(self, 'must have exactly 5 moveables')
        self._mot_rot, self._mot_xv, self._mot_yv, self._mot_xh, \
            self._mot_yh = self._attached_moveables
        self.valuetype = oneof(*sorted(self.mapping, key=num_sort))

    def _generateSequence(self, target):  # pylint: disable=arguments-differ
        seq = []
        targets = self.mapping[target]
        rot_target, xv_target, xh_target, yv_target, yh_target = targets
        # move translation units to move pos (in parallel)
        seq.append(tuple(SeqDev(m, p) for (m, p)
                         in zip(self._attached_moveables[1:], self.movepos)))
        # move rotation stage
        seq.append(SeqDev(self._mot_rot, rot_target))
        # move Y axes to final position with backlash
        seq.append((SeqDev(self._mot_yv, yv_target + 0.1),
                    SeqDev(self._mot_yh, yh_target + 0.1)))
        seq.append(SeqDev(self._mot_yv, yv_target))
        seq.append(SeqDev(self._mot_yh, yh_target))
        # move X axes to 0.1 and then to final position
        seq.append((SeqDev(self._mot_xv, 0.1),
                    SeqDev(self._mot_xh, 0.1)))
        seq.append(SeqDev(self._mot_xv, xv_target))
        seq.append(SeqDev(self._mot_xh, xh_target))
        # move rotation stage again, if it changed
        seq.append(SeqDev(self._mot_rot, rot_target))
        return seq

    def doStart(self, target):
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])
        self._startSequence(self._generateSequence(target))


class Polarizer(Moveable):
    """Controls both the position of the polarizer and the spin flipper.
    """

    valuetype = oneof(*POL_SETTINGS)

    hardware_access = False

    attached_devices = {
        'switcher': Attach('polarizer in/out switch', Moveable),
        'flipper':  Attach('flipper', Moveable),
    }

    parameters = {
        'values':   Param('Possible values (for GUI)', userparam=False,
                          type=listof(str), default=POL_SETTINGS),
    }

    parameter_overrides = {
        'fmtstr':   Override(default='%s'),
        'unit':     Override(mandatory=False, default=''),
    }

    def doRead(self, maxage=0):
        switcher_pos = self._attached_switcher.read(maxage)
        flipper_pos = self._attached_flipper.read(maxage)
        if switcher_pos == 'unknown' or flipper_pos == 'unknown':
            return 'unknown'
        if switcher_pos == 'ng':
            return 'out'
        # Polarizer is a transmission supermirror => without flipper we get
        # the "down" polarization.
        if flipper_pos == 'on':
            return 'up'
        return 'down'

    def doStart(self, target):
        switch_pos = self._attached_switcher.read(0)
        if target == 'out':
            if switch_pos != 'ng':
                self._attached_switcher.start('ng')
            self._attached_flipper.start('off')
        else:
            if switch_pos != 'pol':
                self._attached_switcher.start('pol')
            if target == 'up':
                self._attached_flipper.start('on')
            elif target == 'down':
                self._attached_flipper.start('off')
