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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Module for MIEZE operation."""

import copy
from itertools import chain

from nicos import session
from nicos.core import dictof, listof, anytype, usermethod, Moveable, Param, \
    Override, Value, NicosError
from nicos.utils import printTable
from nicos.pycompat import integer_types


class MiezeMaster(Moveable):

    parameters = {
        'setting':    Param('Current setting', type=int, settable=True),
        'tuning':     Param('Current tuning', type=str, settable=True,
                            category='instrument', default=''),
        'curtable':   Param('Current tuning table', settable=True,
                            type=listof(dictof(str, anytype))),
        'tunetables': Param('Tuning tables for MIEZE settings',
                            type=dictof(str, listof(dictof(str, anytype))),
                            settable=True),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False, default=''),
        'fmtstr': Override(default='%s'),
    }

    def doRead(self, maxage=0):
        if not self.tuning:
            return ['<no tuning selected>', 0.0]
        return [self.curtable[self.setting]['_name_'],
                self.curtable[self.setting]['_tau_']]

    def valueInfo(self):
        return Value('mieze', fmtstr='%s'), \
            Value('tau', fmtstr='%.2f', unit='ps')

    def _findsetting(self, target):
        if not self.tuning:
            raise NicosError(self, 'no tuning selected, use %s.usetuning(name)'
                             ' to select a tuning table' % self)
        if not isinstance(target, integer_types):
            for idx, setting in enumerate(self.curtable):
                if setting['_name_'] == target:
                    target = idx
                    break
            else:
                raise NicosError(self, 'no such MIEZE setting: %r' % (target,))
        if not 0 <= target < len(self.curtable):
            raise NicosError(self, 'no such MIEZE setting: %r' % target)
        return target

    def doStart(self, target):
        index = self._findsetting(target)
        setting = self.curtable[index]
        devs = sorted(setting.items())
        for devname, devvalue in devs:
            if devname.startswith('amp'):
                self.log.debug('moving %r to %r', devname, 0)
                dev = session.getDevice(devname)
                dev.move(0)
        for devname, devvalue in devs:
            if devname.startswith('_') or devname.startswith('amp'):
                continue
            self.log.debug('moving %r to %r', devname, devvalue)
            dev = session.getDevice(devname)
            dev.move(devvalue)
        for devname, devvalue in devs:
            if not devname.startswith('amp'):
                continue
            self.log.debug('moving %r to %r', devname, devvalue)
            dev = session.getDevice(devname)
            dev.move(devvalue)
        self.setting = index

    def doWriteTuning(self, value):
        if value not in self.tunetables:
            raise NicosError(self, 'no such tuning: %r' % value)
        self.curtable = self.tunetables[value]

    @usermethod
    def usetuning(self, name):
        """Use the given tuning table."""
        self.tuning = name

    @usermethod
    def listtunings(self):
        """List all existing tuning tables."""
        data = []
        for name, table in self.tunetables.items():
            data.append((name,
                         ', '.join(setting['_name_'] for setting in table)))
        self.log.info('all tuning tables:')
        printTable(('name', 'settings'), data, session.log.info)

    @usermethod
    def printtuning(self):
        """Print out the current tuning table."""
        data = []
        valueidx = {}
        all_values = set()
        for setting in self.curtable:
            all_values.update(key for key in setting if not key.startswith('_'))
        all_values = sorted(all_values)
        valueidx = dict((val, idx) for idx, val in enumerate(all_values))
        for idx, setting in enumerate(self.curtable):
            values = ['---'] * len(all_values)
            for devname, devvalue in setting.items():
                if not devname.startswith('_'):
                    values[valueidx[devname]] = str(devvalue)[:15]
            data.append((str(idx), setting['_name_'], '%.3f' %
                         setting['_tau_']) + tuple(values))
        self.log.info('current MIEZE settings (%s):', self.tuning)
        printTable(('#', 'name', 'tau (ps)') + tuple(all_values), data,
                   session.log.info)

    @usermethod
    def savetuning(self, name):
        """Save the current tuning table."""
        if name in self.tunetables:
            raise NicosError(self, 'tuning with this name exists already, '
                             'please use removetuning() first')
        tables = self.tunetables.copy()
        tables[name] = copy.deepcopy(self.curtable)
        self.tunetables = tables
        self.log.info('current tuning saved as %r', name)

    @usermethod
    def removetuning(self, name):
        """Delete a tuning table."""
        if name not in self.tunetables:
            raise NicosError(self, 'tuning %r not found in tables' % name)
        tables = self.tunetables.copy()
        del tables[name]
        self.tunetables = tables
        self.log.info('tuning %r removed', name)

    @usermethod
    def newsetting(self, name, **values):
        """Add a new setting to the current tuning table."""
        table = self.curtable[:]
        try:
            index = self._findsetting(name)
            setting = table[index].copy()
        except NicosError:
            if not self.tuning:
                raise
            index = len(table)
            table.append({'_name_': name, '_tau_': 0})
            setting = table[index]
        for devname, devvalue in values.items():
            setting[devname] = devvalue
        table[index] = setting
        self.curtable = table
        self.log.info('created new MIEZE setting %r with index %s',
                      name, index)

    @usermethod
    def updatesetting(self, name, **values):
        """Update a setting in the current tuning table."""
        index = self._findsetting(name)
        table = self.curtable[:]
        setting = table[index].copy()
        for devname, devvalue in values.items():
            setting[devname] = devvalue
        table[index] = setting
        self.curtable = table
        self.log.info('tuning for MIEZE setting %r updated',
                      table[index]['_name_'])

    @usermethod
    def removesetting(self, name):
        """Remove a setting from the current tuning table."""
        index = self._findsetting(name)
        table = self.curtable[:]
        setting = table.pop(index)
        self.curtable = table
        self.log.info('removed MIEZE setting %r', setting['_name_'])

    @usermethod
    def ordersettings(self, *names):
        """Reorder the settings in the current tuning table.

        Usage example::

            mieze.ordersettings('46_69', '72_108', '200_300')
        """
        indices = [self._findsetting(n) for n in names]
        other_indices = set(range(len(self.curtable))) - set(indices)
        new_table = [self.curtable[i] for i in chain(indices, other_indices)]
        self.curtable = new_table
