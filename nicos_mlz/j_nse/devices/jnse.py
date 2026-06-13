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

from nicos import session
from nicos.core import anytype, Attach, dictof, listof, Param, oneof, \
    Override, SubscanMeasurable, status
from nicos.core.constants import MASTER
from nicos.core.device import Measurable, Moveable, Readable
from nicos.core.mixins import DeviceMixinBase, HasMapping, HasPrecision
from nicos.core.scan import Scan
from nicos.core.utils import multiStatus
from nicos.devices.entangle import PowerSupply
from nicos.utils import num_sort
from nicos_mlz.j_nse.devices.instrument import JnseInstrument


class HasLabel(DeviceMixinBase):
    """For devices that store additional label parameter."""

    parameters = {
        'label': Param('Device label from NIST table',
                       type=str, default='', internal=True,),
    }

    def doReadLabel(self):
        try:
            label = session.instrument.devices.get(self.name, '')
        except AttributeError:
            label = ''
        return label


class JNSEPowerSupply(HasLabel, PowerSupply):
    """PowerSupply that stores additional label."""


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
        if self._mode == MASTER:
            self.curvalue = target

    def doStatus(self, maxage=0):
        return status.OK, 'idle'


class NestMapped(HasMapping, Basic):
    """A node in a tree of nested mappings.

    Each node holds a ``mapping`` dict whose values are themselves dicts keyed
    by attached device names. Moving the node to a key propagates the
    corresponding sub-mapping to each ``nextnodes`` child (so their own
    ``mapping`` and ``valuetype`` are updated) and simultaneously drives all
    ``controlled`` devices to their mapped setpoints.

    Leaf nodes (no ``nextnodes``) do not need ``nextnodes`` configured.
    The root node is provided by :class:`NestHead`, which seeds the mapping
    from the instrument table on startup.

    If an ``aliased`` device is attached, it receives the same target value
    on every move, mirroring this node's logical position.
    """

    attached_devices = {
        'aliased': Attach(
            'Device to mirror the current value', devclass=Moveable, optional=True,
        ),
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

    def doInit(self, mode):
        if mode == MASTER:
            self.valuetype = oneof(*sorted(self.mapping, key=num_sort))

    def doStart(self, target):
        if self._mode == MASTER:
            for node in self._attached_nextnodes:
                node.mapping = self.mapping[target][node.name]
                node.valuetype = oneof(*sorted(node.mapping, key=num_sort))
            for dev in self._attached_controlled:
                dev.start(self.mapping[target][dev.name])
            if self._attached_aliased is not None:
                self._attached_aliased.start(target)
        Basic.doStart(self, target)

    def doStatus(self, maxage=0):
        curstatus = multiStatus(self._attached_controlled, maxage)
        if curstatus[0] == status.OK:
            msg = []
            for dev in self._attached_controlled:
                target = self.mapping[self.curvalue][dev.name]
                tol = getattr(dev, 'precision', None) or 0.0
                if not math.isclose(dev.read(maxage), target, abs_tol=tol):
                    msg.append(f'{dev.name} != {target} {dev.unit}')
            if msg:
                curstatus = status.WARN, ', '.join(msg)
        return curstatus


class NestHead(NestMapped):
    """Root node of the nested-mapping tree, seeded from the instrument table.

    On initialization, reads the instrument's configuration table and uses it
    as the top-level mapping (keyed by table filename). Sub-mappings for all
    ``nextnodes`` children are propagated immediately, and the node is moved
    to the current table so all controlled devices reflect the loaded settings.
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
            for node in self._attached_nextnodes:
                node.mapping = self.mapping[fn][node.name]
            NestMapped.doInit(self, mode)
            self.start(fn)


class ScanningDetector(SubscanMeasurable):
    """NSE detector that performs a phase scan as a subscan.

    For each measurement, executes an internal scan stepping the first phase
    power supply (``pha1``) through ``ph_n`` positions while controlling the
    spin-flipper coils (``pi``, ``pi21``, ``pi22``). The phase positions and
    flipper setpoints are derived from the current lambda and tau values via
    their mapping tables.

    Preset parameters:

    - ``ph_n``:   total number of phase steps
    - ``p_down``: number of steps with down-flipper coils active (pi21/pi22
                  set to tau-mapped values)
    - ``p_up``:   number of steps with only pi active (pi21/pi22 zeroed)
    - ``ph_step``: phase increment per step in degrees

    Steps from ``p_up`` to ``ph_n`` have all flipper coils set to zero.
    Any additional preset keys are forwarded to the underlying detector.
    """

    attached_devices = {
        'detector': Attach('Detector to scan', Measurable),
        'lmbda': Attach('Lambda device', Readable),
        'tau': Attach('Tau device', Readable),
    }

    parameters = {
        'pha1': Param(
            'Phase power supply', type=str, mandatory=True, settable=True,
        ),
        'pi': Param(
            'Flipper pi', type=str, mandatory=True, settable=True,
        ),
        'pi21': Param(
            'Flipper pi21', type=str, mandatory=True, settable=True,
        ),
        'pi22': Param(
            'Flipper pi22', type=str, mandatory=True, settable=True,
        ),
        'readresult': Param(
            'Storage for processed results from detector, to be returned from doRead()',
            type=listof(anytype), settable=True, internal=True,
        ),
    }

    def doInit(self, mode):
        if mode == MASTER:
            self._lastpreset = {}
            self._lambda = self._attached_lmbda
            self._tau = self._attached_tau
            self._pha1 = session.getDevice(self.pha1)
            self._pi = session.getDevice(self.pi)
            self._pi21 = session.getDevice(self.pi21)
            self._pi22 = session.getDevice(self.pi22)

    def presetInfo(self):
        return {'ph_n', 'p_down', 'p_up', 'ph_step'} | \
            set(self._attached_detector.presetInfo())

    def doSetPreset(self, **preset):
        self._lastpreset = preset
        self._ph_n = preset.get('ph_n')
        self._p_down = preset.get('p_down')
        self._p_up = preset.get('p_up')
        self._ph_step = preset.get('ph_step')

    def doStart(self):
        l = self._lambda.read()
        t = self._tau.read()
        positions = [
            [self._tau.mapping[t][self.pha1] +
                 self._ph_step / self._lambda.mapping[l]['phase_deg_perA1'] *
                 (p + 1 - math.ceil(self._p_down / 2)),
             self._tau.mapping[t][self.pi21],
             self._tau.mapping[t][self.pi22],
             self._tau.mapping[t][self.pi]]
            for p in range(self._p_down)
        ]
        for _ in range(self._p_down, self._p_up):
            positions += [[positions[-1][0], 0, 0, self._tau.mapping[t][self.pi]]]
        for _ in range(self._p_up, self._ph_n):
            positions += [[positions[-1][0], 0, 0, 0]]
        preset = {k: v for k, v in self._lastpreset.items()
                  if k not in ['ph_n', 'p_down', 'p_up', 'ph_step']}
        # pylint: disable=unused-variable
        ds = Scan(
            [self._pha1, self._pi21, self._pi22, self._pi], positions,
            detlist=[self._attached_detector], subscan=True, preset=preset
        ).run()
        self.readresult = []

    def valueInfo(self):
        res = []
        return tuple(res)

    def doRead(self, maxage=0):
        return self.readresult
