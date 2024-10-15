# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#   Mark Koennecke    <mark.koennecke@psi.ch>
#
# *****************************************************************************
from time import time as currenttime

from nicos import session
from nicos.core import POLLER, SIMULATION, DeviceMixinBase, Override
from nicos.devices.epics.pyepics import EpicsDevice


class PVMonitor(DeviceMixinBase):
    """
    This mixin provides the basic methods required to use the EpicsDevice in
    monitor mode.
    """

    parameter_overrides = {
        'pollinterval': Override(default=None, userparam=False,
                                 settable=False),
        'maxage': Override(default=43202, userparam=False, settable=False)
        }

    def doInit(self, mode):
        """
        Register the update callback for all the PVs.
        """
        if mode != SIMULATION:
            self._register_pv_callbacks()
            for pv in self._pvs.values():
                pv.run_callbacks()

    def doReadPV(self, pvparam, as_string=False):
        """
        Return the value of the parameter. If a monitor is used tries to
        always trust the cache, else uses a PV.get().
        :param pvparam: the name of the PV
        :param as_string: force the return value to be a string
        :return: the current value of the PV
        """

        def _get_value(maxage=None):
            return EpicsDevice._get_pv(self, pvparam, as_string=as_string)

        corresponding_cache_key = self.pv_cache_relations.get(pvparam,
                                                              pvparam)
        val = self._getFromCache(corresponding_cache_key, _get_value)
        return val

    def _register_pv_callbacks(self, update_cb=None):
        if session.sessiontype != POLLER:
            pv_parameters = self._get_pv_parameters()
            for pvparam in pv_parameters:
                self._register_pv_update_callback(
                        pvparam,
                        _on_value_change_cb=update_cb)

    def _on_connection_cb(self, pv_name=None, conn=None, **kws):
        """
        Define a callback that reacts to PV's connection/disconnection.
        :param pv_name: the PV name
        :param conn: connection status (True/False)
        :param kws: optional keyword-only parameters
        """
        if conn:
            self.log.debug('Connected to PV: %r' % pv_name)
        else:
            self.log.warning('Disconnected from PV: %r' % pv_name)

#    def _status_cb(self, pvname=None, value=None, char_value=None, **kws):
#        # The default 'on_value_change' cb already register the change. It's
#        # enough to force a reload of status()
#        self.status()

    def _register_pv_update_callback(self, pvparam, _on_value_change_cb=None,
                                     **kws):
        """
        Allow to register further '_on_value_change' and '_on_connection'
        callbacks.
        :param pvparam: the PV name
        :param _on_connect_cb: callback that is triggered by
        connections/disconnections
        :param _on_change_cb: callback that is triggered by value change
        :param kws: optional keyword-only parameters
        """

        def update_callback(pvparam=None, value=None, char_value=None, **kws):
            """
            Define a callback that reacts to PV's value change. the defaul
            behaviour is to update value stored in the NICOS cache.
            :param pv_name: the PV name
            :param value: the new PV value
            :param char_value: the new PV value in string format
            :param kws: optional keyword-only parameters
            """
            corresponding_cache_key = self.pv_cache_relations.get(pvparam,
                                                                  pvparam)
#            self.log.warning('\tEPICS monitor: %s (%s) -> %r' % (pvparam,
#                                                      corresponding_cache_key,
#                                                      value))
#
            self._cache.put(self._name, corresponding_cache_key,
                            char_value if kws['type'] == 'time_char' else
                            value, kws['timestamp'] or currenttime())

        self._pvs[pvparam].add_callback(
            callback=_on_value_change_cb or update_callback, pvparam=pvparam,
            kws=kws)
