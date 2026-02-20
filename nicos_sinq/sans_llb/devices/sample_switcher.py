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

from nicos.core import Moveable, Override, Param, PositionError,  dictof, listof, status, usermethod
from nicos.core.constants import SLAVE
from nicos.core.params import Attach, oneof
from nicos.devices.abstract import MappedMoveable, MappedReadable


class SampleSwitcher(MappedMoveable):
    """Similar to Switcher for specific sample positions using a set of pre-defined sample holders. In addition to the axis
        that changes the sample there is a perpendicular axis whos value is stored during adjustment.
        Positions are always integers starting at 0::

        move(changer_switch, 1)
        move(changer_switch, 15)
    """
    parameter_overrides = {
        'mapping': Override(description='Mapping of sample ID to move location, updated when adjusted',
                            type=dictof(int, float), settable=True, userparam=False),
        'fmtstr': Override(default='%i'),
        }

    attached_devices = {
        'switch_axis': Attach('The continuous device which is controlled',
                           Moveable),
        'perp_axis': Attach('The perpendicular axis that is just moved back to the adjusted location',
                           Moveable),
        }

    parameters = {
        'precision':    Param('Precision for comparison', default=0.1),
        'current_holder': Param('Select which holder is installed', default='mfu', settable=True,
                                userparam=True, type=oneof('mfu', 'qs110', 'qs120', 'qs404', 'solid', 'olaf')),
        'adjusted_positions': Param(description='Mapping of sample ID to move location, updated when adjusted',
                                       type=dictof(str, listof(float)), settable=True, userparam=False),
        'sample_names': Param('List of sample names to be configured', internal=True, type=listof(str),
                              settable=True, userparam=False),
    }

    # Basic configuration for existin sample holders:
    # number of samples on holder, spacing of samples in mm
    # First sample holder is on the +x side movement, so translation to higher numbers is negative
    holder_dict = {
        'mfu': [9, -41],
        'qs110': [23, -21.5],
        'qs120': [17, -29],
        'qs404': [17, -29],
        'solid': [16, -31],
        'olaf': [10, -39]
    }


    hardware_access = False

    def doInit(self, mode):
        self._update_mapping(self.current_holder)
        MappedReadable.doInit(self, mode)

    def _startRaw(self, target):
        """Initiate movement of the moveable to the translated raw value."""
        self._attached_perp_axis.start(self.adjusted_positions[self.current_holder][1])
        self._attached_switch_axis.start(target)

        tgidx = self._mapReadValue(target)
        if self.sample_names[tgidx]:
            # if configured, update sample name to new one
            if self._cache:
                self._cache.put('sample', 'value', self.sample_names[tgidx])
                self._cache.put('sample', 'samplename', self.sample_names[tgidx])
                samples = dict(self._cache.get('sample', 'samples'))
                sample0 = dict(samples[0])
                sample0['name']= self.sample_names[tgidx]
                samples[0] = sample0
                self._cache.put('sample', 'samples', samples)

    def _readRaw(self, maxage=0):
        """Return raw position value of the moveable."""
        return self._attached_switch_axis.read(maxage)

    def _mapReadValue(self, value):
        """Override default inverse mapping to allow a
        deviation <= precision.
        """
        prec = self.precision
        for name, pos in self.mapping.items():
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        return -1

    def doIsAllowed(self, target):
        # Forward the move request to the underlying device
        return self._attached_switch_axis.isAllowed(self._mapTargetValue(target))

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        (move_status, move_msg) = self._attached_switch_axis.status(maxage)
        if move_status == status.BUSY:
            return move_status, f'moving to {self.format(self.target)}'
        elif move_status not in (status.OK, status.WARN):
            return (move_status, move_msg)

        # otherwise, we have to check if we are at a known position,
        # and otherwise return an error status
        try:
            r = self.read(maxage)
            if r not in self.mapping:
                if self.fallback:
                    return (status.UNKNOWN, 'unconfigured position of %s, '
                            'using fallback' % self._attached_switch_axis)
                return (status.NOTREACHED, 'unconfigured position of %s or '
                        'still moving' % self._attached_switch_axis)
        except PositionError as e:
            return status.NOTREACHED, str(e)
        return status.OK, f'{self.current_holder}'

    def doReset(self):
        self._attached_switch_axis.reset()
        self._attached_perp_axis.reset()

    def doStop(self):
        self._attached_switch_axis.stop()
        self._attached_perp_axis.stop()

    @usermethod
    def store(self):
        '''
        Save adjusted position for this holder, the closest sample will be used to determine offset.
        '''
        #
        # find best fitting sample location
        value = self._attached_switch_axis.read()
        posval = []
        for name, pos in self.mapping.items():
            posval.append((abs(pos - value), pos, name))
        posval.sort()
        _, pos, name = posval[0]

        new_adj = {}

        for key, params in self.adjusted_positions.items():
            if key==self.current_holder:
                new_adj[key] = [value-pos+params[0], self._attached_perp_axis.read()]
            else:
                new_adj[key] = params
        self.adjusted_positions = new_adj
        self._update_mapping(self.current_holder)
        self.poll()

    def _update_mapping(self, value):
        # replace mapping in dependence of selected sample holder
        if self._mode==SLAVE:
            return
        N, space = self.holder_dict[value]
        new_mapping = {}
        inverse_mapping = {}
        ap = self.adjusted_positions[value]
        for i in range(N):
            pos = i*space+ap[0]
            new_mapping[i] = pos
            inverse_mapping[pos] = i
        self.mapping = new_mapping
        self._inverse_mapping = inverse_mapping

    def doWriteMapping(self, mapping):
        # update the valuetype options when mapping changes
        self.valuetype = oneof(*mapping)

    def doWriteCurrent_Holder(self, value):
        if value in self.holder_dict:
            # change of the sample holder
            self._update_mapping(value)
            self.sample_names = ['' for i in range(self.holder_dict[value][0])]
            return value
        else:
            raise ValueError("current_holder needs to be one of %s"%list(self.holder_dict.keys()))

    def __getitem__(self, item):
        return self.sample_names[item]

    def __setitem__(self, index, value):
        # update one sample name
        lst = list(self.sample_names)
        lst[index] = value
        self.sample_names = lst
