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

from nicos import session
from nicos.core.device import Moveable, Override, Param, anytype, dictof, \
    listof, tupleof, usermethod
from nicos.core.errors import ConfigurationError
from nicos.core.utils import multiStatus
from nicos.utils import printTable


class StoredPositions(Moveable):
    """
    This is a more generalized mapped moveable in that it can
    store arbitrary device positions. Also, the mappings are
    editable at runtime.
    """

    parameters = {
        'positions': Param('dictionary with mappings of keys to '
                           'device positions',
                           type=dictof(str, listof(tupleof(str, anytype))),
                           settable=True,
                           category='general'),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='name'),
    }

    valuetype = str
    _wait_list = []

    def _adddev(self, name, rval=Ellipsis):
        try:
            dev = session.getDevice(name, Moveable)
        except ConfigurationError:
            session.log.error('%s is no known device', name)
            return None
        if rval == Ellipsis:
            rval = dev.read(0)
        else:
            ok, _ = dev.isAllowed(rval)
            if not ok:
                session.log.error('%s is no valid target for %s',
                                  str(rval), name)
                return None
        return name, rval

    @usermethod
    def define_position(self, name, *args, **kwds):
        """
        Add a stored position to the dictionary
        :param name: The key used to reference the stored position henceforth
        :param args: A list of tuples (devicename, position) or only
        devicenames. In the latter case the position is the current position of
        the device
        """
        maplist = []
        for a in args:
            if isinstance(a, tuple):
                mp = self._adddev(a[0], a[1])
            else:
                mp = self._adddev(a)
            if mp:
                maplist.append(mp)
            else:
                return
        for devn, rval in kwds.items():
            mp = self._adddev(devn, rval)
            if mp:
                maplist.append(mp)
            else:
                return
        rwdict = dict(self.positions)
        rwdict[name] = maplist
        self.positions = rwdict

    @usermethod
    def clear(self):
        """
         Delete all stored positions
        """
        self.positions = {}

    @usermethod
    def delete(self, name):
        """
        Deletes a named stored position
        :param name: The name of the stored position to delete
        """
        rwdict = dict(self.positions)
        del rwdict[name]
        self.positions = rwdict

    @usermethod
    def show(self):
        """
        Shows the list of stored positions
        """
        session.log.info('Stored positions on %s\n', self.name)
        items = []
        for key, val in self.positions.items():
            items.append((key, str(val)))
        printTable(('Name', 'Device positions'), items, session.log.info)

    def doStart(self, target):
        if not self.isCompleted():
            self.log.error('Another stored position is already running')
            return
        self._wait_list = []
        for entry in self.positions[target]:
            try:
                dev = session.getDevice(entry[0])
            except ConfigurationError:
                session.log.error('Stored position %s no longer valid, '
                                  'device %s not found', target, entry[0])
                return
            if not dev.isAllowed(entry[1]):
                session.log.error('Cannot drive %s to %s anymore',
                                  entry[0], entry[1])
                return
        for entry in self.positions[target]:
            dev = session.getDevice(entry[0])
            dev.start(entry[1])
            self._wait_list.append(dev)

    def doIsAllowed(self, target):
        if target not in self.positions:
            return False, 'Unknown stored position %s' % target
        ok = True
        whysum = []
        for entry in self.positions[target]:
            try:
                dev = session.getDevice(entry[0])
            except ConfigurationError:
                if ok:
                    ok = False
                whysum.append('%s no longer in configuration' % entry[0])
            allowed, why = dev.isAllowed(entry[1])
            if not allowed:
                if ok:
                    ok = False
                whysum.append(why)
        return ok, ','.join(whysum)

    def doStatus(self, maxage=0):
        return multiStatus(self._wait_list, maxage)

    def _is_at_position(self, entry):
        for pair in entry:
            try:
                dev = session.getDevice(pair[0])
            except ConfigurationError:
                return False
            if abs(dev.read(0) - pair[1]) > dev.precision:
                return False
        return True

    def doRead(self, maxage=0):
        for key, entry in self.positions.items():
            if self._is_at_position(entry):
                return key
        return 'Undefined'

    def doStop(self):
        for dev in self._wait_list:
            dev.stop()

    def doFinish(self):
        for dev in self._wait_list:
            dev.finish()
