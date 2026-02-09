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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos import session
from nicos.core.device import Moveable, Override, Param, anytype, dictof, \
    listof, nicosdev, oneof, status, tupleof, usermethod
from nicos.core.errors import ConfigurationError, UsageError
from nicos.core.utils import multiStatus, multiStop
from nicos.utils import printTable


class StoredPositions(Moveable):
    """A more generalized, dynamically configureable, mapped moveable.

    It can store arbitrary device positions. Also, the mappings are editable at
    runtime.
    """

    parameters = {
        'positions': Param('dictionary with mappings of keys to device '
                           'positions',
                           type=dictof(str, listof(tupleof(nicosdev, anytype))),
                           settable=True, volatile=True, category='general'),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='name'),
    }

    valuetype = oneof([])
    _wait_list = []
    _mapping = {}

    def _adddev(self, name, rval=Ellipsis):
        try:
            dev = session.getDevice(name, Moveable)
        except ConfigurationError as e:
            session.log.error('%s is no known device: %s', name, e)
            return None
        except UsageError as e:
            session.log.error('%s is has wrong type: %s', name, e)
            return None
        if rval == Ellipsis:
            rval = dev.read(0)
        else:
            ok, _ = dev.isAllowed(rval)
            if not ok:
                session.log.error('%s is no valid target for %s',
                                  str(rval), dev.name)
                return None
        return dev.name, rval

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
            if not mp:
                return
            maplist.append(mp)
        for devn, rval in kwds.items():
            mp = self._adddev(devn, rval)
            if not mp:
                return
            maplist.append(mp)
        self._mapping[name] = maplist
        self.valuetype = oneof(*list(self.positions))

    @usermethod
    def clear(self):
        """
         Delete all stored positions
        """
        self._mapping = {}
        self.valuetype = oneof(*list(self.positions))

    @usermethod
    def delete(self, name):
        """
        Deletes a named stored position
        :param name: The name of the stored position to delete
        """
        del self._mapping[name]
        self.valuetype = oneof(*list(self.positions))

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
        for devname, t in self.positions[target]:
            try:
                dev = session.getDevice(devname, Moveable)
            except ConfigurationError:
                session.log.error('Stored position %s no longer valid, '
                                  'device %s not found', target, devname)
                return
            if not dev.isAllowed(t):
                session.log.error('Cannot drive %s to %s anymore', devname, t)
                return
        for devname, t in self.positions[target]:
            dev = session.getDevice(devname, Moveable)
            dev.start(t)
            self._wait_list.append(dev)

    def doIsAllowed(self, target):
        if target not in self.positions:
            return False, 'Unknown stored position %s' % target
        ok = True
        whysum = []
        for devname, t in self.positions[target]:
            try:
                dev = session.getDevice(devname, Moveable)
            except ConfigurationError:
                ok &= False
                whysum.append('%s no longer in configuration' % devname)
            allowed, why = dev.isAllowed(t)
            if not allowed:
                ok &= False
                whysum.append(why)
        return ok, ','.join(whysum)

    def doStatus(self, maxage=0):
        if waiters := self._getWaiters():
            return multiStatus(waiters, maxage)
        return status.OK, ''

    def doRead(self, maxage=0):
        for key, entry in self.positions.items():
            if self._is_at_position(entry):
                return key
        return 'Undefined'

    def doStop(self):
        if self._getWaiters():
            multiStop(self._getWaiters())

    def doFinish(self):
        for dev in self._getWaiters():
            dev.finish()

    def doWritePositions(self, value):
        self.clear()
        for target, conf in value.items():
            self.define_position(target, *conf)

    def doReadPositions(self):
        return self._mapping

    def _is_at_position(self, entry):
        for devname, target in entry:
            try:
                dev = session.getDevice(devname, Moveable)
            except ConfigurationError:
                return False
            if not dev.isAtTarget(target=target):
                return False
        return True

    def _getWaiters(self):
        return self._wait_list
