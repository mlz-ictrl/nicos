#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
import numpy as np

from nicos.core.constants import FINAL
from nicos.core.params import ArrayDesc, Param, Value, pvname
from nicos.core.status import BUSY, OK
from nicos.devices.epics import EpicsDevice
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel


class FastComtecChannel(ImageChannelMixin, EpicsDevice, PassiveChannel):
    """
    This is a data channel for the FastComtec MCA as used with the
    mobile chopper unit. It is characterized by taking a long time
    to actually transfer data.
    """
    parameters = {
        'pvprefix': Param('Prefix of the record PV.', type=pvname,
                          mandatory=True, settable=False, userparam=False),
    }

    _fields = {
        'status': 'Status_RBV',
        'count':  'CNT',
        'nelm': 'NELM_RBV',
        'data': 'Data'
    }

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in area detector image record.

        :return: List of PV aliases.
        """
        pvs = set(self._fields.keys())
        return pvs

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the pvprefix parameter, if necessary.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        prefix = getattr(self, 'pvprefix')
        field = self._fields.get(pvparam)

        if field is not None:
            return ':'.join((prefix, field))

        return getattr(self, pvparam)

    def doStart(self):
        self._put_pv('count', 1)

    def doStop(self):
        self._put_pv('count', 0)

    def doStatus(self, maxage=0):
        raw_status = self._get_pv('status')
        if raw_status == 0:
            return OK, 'Idle'
        elif raw_status == 1:
            return BUSY, 'Counting'
        elif raw_status == 2:
            return BUSY, 'Reading data'
        else:
            raise NotImplementedError('Status %s unknown' % (raw_status))

    def doReadArray(self, quality):
        if quality == FINAL:
            # This thing does not do intermediate data
            nelm = self._get_pv('nelm')
            data = self._pvs['data'].get(count=nelm, timeout=self.epicstimeout)
            return np.array(data)

    def valueInfo(self):
        return Value(self.name, unit=''),

    @property
    def arraydesc(self):
        nelm = self._get_pv('nelm')
        return ArrayDesc(self.name, (nelm,), 'uint32')
