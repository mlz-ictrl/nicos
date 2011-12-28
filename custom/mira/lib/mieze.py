#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

__version__ = "$Revision$"

import copy

from nicos import session
from nicos.utils import dictof, listof, anytype, usermethod, printTable
from nicos.device import Moveable, Param, Override
from nicos.errors import NicosError
from nicos.commands.output import printinfo


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

    def doRead(self):
        if self.tuning == '':
            return '<no tuning selected>'
        return self.curtable[self.setting]['_name_']

    def _findsetting(self, target):
        if self.tuning == '':
            raise NicosError(self, 'no tuning selected') # XXX how to?
        if not isinstance(target, (int, long)):
            for idx, setting in enumerate(self.curtable):
                if setting['_name_'] == target:
                    target = idx
                    break
            else:
                raise NicosError(self, 'no such MIEZE setting: %r' % target)
        if not 0 <= target < len(self.curtable):
            raise NicosError(self, 'no such MIEZE setting: %r' % target)
        return target

    def doStart(self, target):
        index = self._findsetting(target)
        setting = self.curtable[index]
        for devname, devvalue in sorted(setting.iteritems()):
            if devname.startswith('_'):
                continue
            dev = session.getDevice(devname)
            dev.move(devvalue)
            dev.wait()

    def doWriteTuning(self, value):
        if value not in self.tunetables:
            raise NicosError(self, 'no such tuning: %r' % value)
        self.curtable = self.tunetables[value]

    @usermethod
    def usetuning(self, name):
        self.tuning = name

    @usermethod
    def listtunings(self):
        data = []
        for name, table in self.tunetables.iteritems():
            data.append((name,
                         ', '.join(setting['_name_'] for setting in table)))
        self.log.info('all tuning tables:')
        printTable(('name', 'settings'), data, printinfo)

    @usermethod
    def printtuning(self):
        data = []
        valueidx = {}
        all_values = set()
        for setting in self.curtable:
            all_values.update(key for key in setting if not key.startswith('_'))
        all_values = sorted(all_values)
        valueidx = dict((val, idx) for idx, val in enumerate(all_values))
        for idx, setting in enumerate(self.curtable):
            values = ['---'] * len(all_values)
            for devname, devvalue in setting.iteritems():
                if not devname.startswith('_'):
                    values[valueidx[devname]] = str(devvalue)
            data.append((str(idx), setting['_name_']) + tuple(values))
        self.log.info('current MIEZE settings (%s):' % self.tuning)
        printTable(('#', 'name') + tuple(all_values), data, printinfo)

    @usermethod
    def newsetting(self, name, **values):
        table = self.curtable
        try:
            index = self._findsetting(name)
        except NicosError:
            if self.tuning == '':
                raise
            index = len(table)
            table.append({'_name_': name})
        for devname, devvalue in values.iteritems():
            table[index][devname] = devvalue
        self.curtable = table
        self.log.info('created new MIEZE setting %r with index %s' %
                      (name, index))

    @usermethod
    def updatesetting(self, name, **values):
        index = self._findsetting(name)
        table = self.curtable
        for devname, devvalue in values.iteritems():
            table[index][devname] = devvalue
        self.curtable = table
        self.log.info('tuning for MIEZE setting %r updated' %
                      table[index]['_name_'])

    @usermethod
    def removesetting(self, name):
        index = self._findsetting(name)
        table = self.curtable
        setting = table.pop(index)
        self.curtable = table
        self.log.info('removed MIEZE setting %r' % setting['_name_'])

    @usermethod
    def savetuning(self, name):
        if name in self.tunetables:
            raise NicosError(self, 'tuning with this name exists already, '
                             'please use removetuning() first')
        tables = self.tunetables
        tables[name] = copy.deepcopy(self.curtable)
        self.tunetables = tables
        self.log.info('current tuning saved as %r' % name)
        # XXX save to disk somewhere

    @usermethod
    def removetuning(self, name):
        if name not in self.tunetables:
            raise NicosError(self, 'tuning %r not found in tables' % name)
        tables = self.tunetables
        del tables[name]
        self.tunetables = tables
        self.log.info('tuning %r removed' % name)
