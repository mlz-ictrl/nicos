# -*- coding: utf-8 -*-
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
import threading
from time import time as currenttime

import epics

from nicos import session
from nicos.core import POLLER, CommunicationError, DeviceMixinBase, Override, \
    status
from nicos.devices.epics import SEVERITY_TO_STATUS, STAT_TO_STATUS


class PyEpicsMonitor(DeviceMixinBase):
    """
    This mixin provides the basic methods required to use the EpicsDevice in
    monitor mode.

    Classes that uses this mixin *can* override:

    .. method:: _on_value_change_cb(pvparam, value, char_value, status,
                                    severity, **kws)

      Called when the value of a PV changes. The default implementation uses
      status and severity to determine the global epics status and stores the
      PV value in the cache.
      The cache key used is `pvparam` if `pvparam` is not in
      `pv_cache_relations`, else the corresponding map value.

    .. method:: _on_status_change_cb

      Called when the status PVs change. The default implementation computes the
      device status using `doStatus` and stores the result in the cache, under
      the `status` key.

    .. method:: _get_status_parameters

      Returns set of parameters that doStatus has to use to determine the
      device status
    """

    parameter_overrides = {
        'pollinterval': Override(default=86400, userparam=False,
                                 settable=False),
        'maxage': Override(default=43202, userparam=False, settable=False)}

    pv_cache_relations = {'readpv': 'value', 'writepv': 'target',
                          'targetpv': 'target', }
    _mapped_status = {}
    _start_condition = None

    def _wait_for_start(self):
        # Give EPICS time to process start command
        if self._start_condition is None:
            self._start_condition = threading.Condition()
        with self._start_condition:
            self._start_condition.wait(self.epicstimeout)

    def _register_pv_callbacks(self, update_cb=None, connect_cb=None,
                               status_cb=None):
        pv_parameters = self._get_pv_parameters()
        status_parameters = self._get_status_parameters()
        if session.sessiontype == POLLER:
            for pvparam in pv_parameters:
                self._register_pv_update_callback(pvparam,
                                                  _on_value_change_cb=update_cb)
        else:
            for pvparam in status_parameters or pv_parameters:
                self._register_pv_status_callback(pvparam,
                                                  _on_status_change_cb=status_cb)

    def _get_status_parameters(self):
        return set()

    def _on_value_change_cb(self, pvparam=None, value=None, char_value=None,
                            status=None, severity=None, **kws):
        corresponding_cache_key = self.pv_cache_relations.get(
            pvparam) or pvparam
        PyEpicsMonitor._set_mapped_epics_status(self, pvparam, status, severity)

        if 'type' in kws and 'enum' in kws['type']:
            value = kws['enum_strs'][int(value)]

        self._cache.put(self._name, corresponding_cache_key,
                        char_value if kws['type'] == 'time_char' else value,
                        currenttime())

    def _on_status_change_cb(self, pvparam, value=None, char_value='', **kws):
        self._cache.put(self._name, 'status', self.doStatus(), currenttime())
        if self._start_condition:
            with self._start_condition:
                self._start_condition.notifyAll()

    def _on_connection_cb(self, pv_name='', connection=None, **kws):
        if connection:
            self.log.info('Connected to PV: %r' % pv_name)
        else:
            self.log.warning('Disconnected from PV: %r' % pv_name)

    def _register_pv_update_callback(self, pvparam, on_value_change_cb=None,
                                     **kws):
        self._pvs[pvparam].add_callback(
            callback=on_value_change_cb or self._on_value_change_cb,
            pvparam=pvparam, with_ctrlvars=True, kws=kws)

    def _register_pv_status_callback(self, pvparam, on_status_change_cb=None,
                                     **kws):
        self._pvs[pvparam].add_callback(
            callback=on_status_change_cb or self._on_status_change_cb,
            pvparam=pvparam, cv=self._start_condition, kws=kws)

    def _get_pv(self, pvparam, as_string=False):
        def _get_value(maxage=None):
            # This is the original _get_pv. Unfortunately this class doesn't
            # derive from EpicsDevice, hence I can't use something like
            # EpicsDevice._get_pv(self, ...)
            if epics.ca.current_context() is None:
                epics.ca.use_initial_context()
            result = self._pvs[pvparam].get(timeout=self.epicstimeout,
                                            as_string=as_string)
            if result is None:  # timeout
                raise CommunicationError(self, 'timed out getting PV %r from '
                                               'EPICS' % self._get_pv_name(
                    pvparam))
            return result

        corresponding_cache_key = self.pv_cache_relations.get(
            pvparam) or pvparam
        val = self._getFromCache(corresponding_cache_key, _get_value)
        return val

    def _set_mapped_epics_status(self, pvparam, epics_status, epics_severity):
        mapped_status = STAT_TO_STATUS.get(epics_status, None)
        if mapped_status is None:
            mapped_status = SEVERITY_TO_STATUS.get(epics_severity,
                                                   status.UNKNOWN)

        self._mapped_status.setdefault(mapped_status, []).append(
            self._get_pv_name(pvparam))

    def _get_mapped_epics_status(self):
        return max(self._mapped_status.items() or [(status.OK, []), ])
