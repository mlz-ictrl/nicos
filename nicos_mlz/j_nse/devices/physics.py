# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

import math

from nicos.core import Attach, Override, Param, anytype, dictof, oneof, \
    oneof_or, status
from nicos.core.constants import MASTER
from nicos.core.device import Moveable
from nicos.core.mixins import HasLimits, HasMapping, HasPrecision
from nicos.core.utils import multiStatus
from nicos.devices.abstract import TransformedMoveable
from nicos.utils import num_sort

from nicos_mlz.j_nse.devices import JnseInstrument
from nicos_mlz.stressi.devices.mixins import TransformMove


class Basic(HasPrecision, Moveable):
    """Virtual device that can store and read the current value."""

    valuetype = anytype

    parameters = {
        'curvalue': Param(
            'Store the current device value',
            unit='main', internal=True, type=anytype, settable=True,
        ),
    }

    def doRead(self, maxage=0):
        return self.curvalue

    def doStart(self, target):
        self.curvalue = target

    def doStatus(self, maxage=0):
        return status.OK, 'idle'


class NestMapped(HasMapping, Basic):
    """A node in a tree of nested mappings.

    Each node holds a ``mapping`` dict whose values are themselves dicts keyed
    by attached device names. Moving the node to a key passes the matching
    sub-mapping to each ``nextnodes`` child and drives all ``controlled``
    devices to their setpoints from the mapping.

    Only the ``mapping`` keys are accepted as targets. The list of allowed
    values is rebuilt every time ``mapping`` changes, no matter where the
    change comes from.

    The status is the combined status of the ``controlled`` devices. Once all
    of them are idle, it is WARN if any of them is off its setpoint by more
    than its ``precision``, or if the current value is not a ``mapping`` key.
    It is also WARN as long as the ``mapping`` is empty.

    Leaf nodes do not need ``nextnodes`` configured.
    The root node is provided by :class:`NestHead`, which fills the tree from
    the instrument table on startup.
    A node that also accepts values between the keys is provided by
    :class:`NestTransform`.
    """

    attached_devices = {
        'controlled': Attach(
            'Dependant controlled devices', devclass=Moveable, multiple=True,
            optional=True,
        ),
        'nextnodes': Attach(
            'Dependant NestMapped device', devclass=Moveable, multiple=True,
            optional=True,
        ),
    }

    parameter_overrides = {
        'mapping': Override(type=dictof(anytype, anytype), default={},
                            mandatory=False, settable=True),
    }

    def doStart(self, target):
        if target in self.mapping:
            for node in self._attached_nextnodes:
                node.mapping = self.mapping[target][node.name]
            for dev in self._attached_controlled:
                dev.start(self.mapping[target][dev.name])
        Basic.doStart(self, target)

    def doStatus(self, maxage=0):
        curstatus = multiStatus(self._attached_controlled, maxage)
        if curstatus[0] == status.OK:
            if not self.mapping:
                return status.WARN, 'mapping is empty'
            if self.curvalue is not None:
                if self.curvalue not in self.mapping:
                    return (status.WARN, 'non-predefined value '
                                         f'{self.fmtstr % self.curvalue} {self.unit}')
            msg = []
            if self.curvalue is not None:
                for dev in self._attached_controlled:
                    target = self.mapping[self.curvalue][dev.name]
                    tol = getattr(dev, 'precision', None) or 0.0
                    if not math.isclose(dev.read(maxage), target, abs_tol=tol):
                        msg.append(f'{dev.name} != {target} {dev.unit}')
            if msg:
                curstatus = status.WARN, ', '.join(msg)
        return curstatus

    def doUpdateMapping(self, mapping):
        self.valuetype = oneof(*sorted(mapping, key=num_sort))


class NestTransform(HasLimits, TransformMove, TransformedMoveable, NestMapped):
    """A node of the nested-mapping tree that accepts any value within limits.

    Unlike :class:`NestMapped`, the target is not restricted to the ``mapping``
    keys: any value within ``abslimits`` is allowed, and ``userlimits`` always
    equal ``abslimits``. Sub-mappings and ``controlled`` setpoints are only
    passed on for a target that is a mapping key. A value in between is
    accepted, but reported with a WARN status as long as the node stays there.

    An optional ``dev`` device can be attached, with ``informula`` and
    ``outformula`` converting between its values and the values of this node.
    Then the node reads its value from ``dev``, every move also drives ``dev``
    to the converted target, and the status of ``dev`` comes first before the
    status of the ``controlled`` devices. While ``dev`` is idle, the node
    follows it: a read value within ``precision`` of a mapping key is taken
    as that key and its sub-mappings are passed on to the ``nextnodes``.

    The limits are taken from ``dev`` if it has ``abslimits``, converted with
    ``informula``. Otherwise, they are the minimum and maximum of the mapping
    keys. With an empty mapping the limits are zero.
    """

    hardware_access = False

    attached_devices = {
        'dev': Attach(
            'Device to transform values at', devclass=Moveable, optional=True,
        ),
    }

    parameter_overrides = {
        'abslimits': Override(mandatory=False, volatile=True),
        'precision': Override(settable=False, volatile=True),
        'unit': Override(volatile=False, mandatory=True),
        'userlimits': Override(settable=False, volatile=True),
    }

    def doIsAllowed(self, target):
        # limits are checked by HasLimits; skip the mapping-key check
        return True, ''

    def _matchKey(self, value):
        for key in self.mapping:
            if math.isclose(key, value, abs_tol=self.precision):
                return key
        return None

    def doPoll(self, n, maxage):
        if self._attached_dev is None:
            return None
        if self._attached_dev.status(maxage)[0] != status.OK:
            return None
        value = TransformedMoveable.doRead(self, maxage)
        key = self._matchKey(value)
        newvalue = value if key is None else key
        if self.curvalue is not None and \
                math.isclose(newvalue, self.curvalue, abs_tol=self.precision):
            return None
        self._setROParam('curvalue', newvalue)
        if key is not None:
            for node in self._attached_nextnodes:
                node._setROParam('mapping', self.mapping[key][node.name])
        return None

    def doRead(self, maxage=0):
        if self._attached_dev is not None:
            return TransformedMoveable.doRead(self, maxage)
        return Basic.doRead(self, maxage)

    def _limits(self, mapping):
        if self._attached_dev is not None \
                and hasattr(self._attached_dev, 'abslimits'):
            rawlimits = self._attached_dev.abslimits
            try:
                limits = [self._mapReadValue(v) for v in rawlimits]
            except (ArithmeticError, ValueError, TypeError) as err:
                self.log.warning('cannot derive absolute limits from %s limits '
                                 '%s: %s', self._attached_dev, rawlimits, err)
                return 0, 0
            return min(limits), max(limits)
        if not mapping:
            return 0, 0
        return min(mapping), max(mapping)

    def doReadAbslimits(self):
        return self._limits(self.mapping)

    def doReadPrecision(self):
        praw = getattr(self._attached_dev, 'precision', None)
        if not praw:
            return 0.0
        x = self._attached_dev.read()
        try:
            return abs(self._mapReadValue(x + praw) - self._mapReadValue(x))
        except (ArithmeticError, ValueError, TypeError) as err:
            self.log.warning('cannot derive precision from %s: %s',
                             self._attached_dev, err)
            return 0.0

    def doReadUserlimits(self):
        return self.abslimits

    def doReadUnit(self):
        return self._config.get('unit', '')

    def doStart(self, target):
        if self._attached_dev is not None:
            TransformedMoveable.doStart(self, target)
        NestMapped.doStart(self, target)

    def doStatus(self, maxage=0):
        curstatus = status.OK, ''
        if self._attached_dev is not None:
            curstatus = self._attached_dev.status(maxage)
        if curstatus[0] == status.OK:
            return NestMapped.doStatus(self, maxage)
        return curstatus

    def doUpdateMapping(self, mapping):
        if not mapping:
            self.valuetype = float
            return
        self.valuetype = oneof_or(sorted(mapping, key=num_sort), float)


class NestHead(NestMapped):
    """Root node of the nested-mapping tree, filled from the instrument table.

    On startup, reads the instrument's settings table and uses it as the
    top-level mapping, keyed by the table filename. The node is then moved to
    that filename, which passes the sub-mappings down the tree and drives all
    controlled devices to the loaded settings.
    """

    attached_devices = {
        'instrument': Attach(
            'Instrument object', devclass=JnseInstrument, optional=True,
        ),
    }

    def doInit(self, mode):
        if mode == MASTER:
            fn = self._attached_instrument.table_filename
            self.mapping = {fn: self._attached_instrument.table}
            self.start(fn)
