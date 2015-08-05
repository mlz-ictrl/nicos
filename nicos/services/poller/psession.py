#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Session class used with the NICOS poller."""

from nicos.core import Device, Override, DeviceAlias, POLLER
from nicos.core.sessions.simple import NoninteractiveSession
from nicos.devices.generic.cache import CacheReader
from nicos.devices.cacheclient import CacheClient
from nicos.protocols.cache import OP_TELL, cache_load


class PollerCacheClient(CacheClient):
    """Special cache client for the poller.

    Callbacks are normally only called for cache updates that are sent to
    us, but not updates we send to the cache.

    For the poller, we want callbacks (that trigger polling of superdevices
    among other things) to be called even if the update comes from this
    process (i.e. another thread calling another device).
    """

    remote_callbacks = False  # no "normal" callbacks on remote updates

    # but use _propagate to call callbacks always
    def _propagate(self, args):
        time, key, op, value = args
        if op == OP_TELL and key in self._callbacks and value:
            self._call_callbacks(key, cache_load(value), time)


class PollerCacheReader(CacheReader):
    parameter_overrides = {
        'unit' : Override(mandatory=False),
    }

    def _initParam(self, param, paraminfo=None):
        # This method is called on init when a parameter is not in the cache.
        # In this case we don't want to do anything here since we don't want
        # to overwrite parameters shared by CacheReader and the real device
        # in the cache with the default values -- the poller shouldn't need
        # the parameters anyway.
        pass


class PollerSession(NoninteractiveSession):

    cache_class = PollerCacheClient
    sessiontype = POLLER

    # pylint: disable=W0102
    def getDevice(self, dev, cls=None, source=None,
                  replace_classes=[(DeviceAlias, PollerCacheReader, {})]):
        """Override device creation for the poller.

        With the "alias device" mechanism, aliases can point to any device in
        the currently loaded setups.  This leads to a problem with the poller,
        since the poller loads each setup in a different process, and in the
        process that polls the DeviceAlias, the pointee can be missing.

        Therefore, we replace devices that are not found by a CacheReader, in
        the hope that the actual pointee is contained in another setup that is
        polled by another process, and we can get current values for the device
        via the CacheReader.
        """
        return NoninteractiveSession.getDevice(self, dev, Device, source,
                                               replace_classes=replace_classes)

    # do not send action messages to the cache

    def beginActionScope(self, what):
        pass

    def endActionScope(self):
        pass

    def action(self, what):
        pass
