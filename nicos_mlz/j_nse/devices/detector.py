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
from nicos.core import anytype, Attach, listof, Param, SubscanMeasurable
from nicos.core.constants import MASTER
from nicos.core.device import Measurable, Readable
from nicos.core.scan import Scan


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
