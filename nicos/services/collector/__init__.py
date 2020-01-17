#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""The NICOS cache collector daemon."""

from __future__ import absolute_import, division, print_function

import re

from nicos.core import Attach, Override, Param
from nicos.core.device import Device
from nicos.core.errors import ConfigurationError
from nicos.core.mixins import DeviceMixinBase
from nicos.core.params import dictof, listof, oneof
from nicos.devices.cacheclient import BaseCacheClient
from nicos.protocols.cache import OP_TELL, OP_TELLOLD
from nicos.utils import createThread
from nicos.pycompat import queue

try:
    import requests
except ImportError:
    requests = None

try:
    import simplejson as json
except ImportError:
    import json


PREFIX_RE = re.compile(r'[a-zA-Z0-9_/]+\.\*$')


class CacheKeyFilter(DeviceMixinBase):
    """Mixin for filtering cache keys that might be forwarded.

    This is used on the source side (Collector device), as well as on
    individual sinks (ForwarderBase devices) for maximum flexibility.
    """

    parameters = {
        'keyfilters': Param('Filter keys to send (regexps); if empty, all '
                            'keys are accepted', type=listof(str)),
    }

    def _initFilters(self):
        self._prefixfilters = ()
        self._regexfilters = []
        for regex in self.keyfilters:
            # special case: prefixes
            if PREFIX_RE.match(regex):
                self._prefixfilters += (regex[:-2],)
            else:
                self._regexfilters.append(re.compile(regex))

    def _checkKey(self, key):
        if not self._prefixfilters and not self._regexfilters:
            return True
        if key.startswith(self._prefixfilters):
            return True
        for keyfilter in self._regexfilters:
            if keyfilter.match(key):
                return True
        return False


class ForwarderBase(CacheKeyFilter, DeviceMixinBase):
    """Defines the interface for a sink that forwards cache updates to an
    external service.
    """

    def _startWorker(self):
        pass

    def _putChange(self, time, ttl, key, value):
        pass


class CacheForwarder(ForwarderBase, BaseCacheClient):
    """Forwards cache updates to another cache.

    The `prefix` parameter of this device can be set to something other than
    `nicos/` to put keys from various sources into unique namespaces.
    """

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        self._initFilters()

    def _connect_action(self):
        # send no requests for keys or updates
        pass

    def _startWorker(self):
        self._worker.start()

    def _putChange(self, time, ttl, key, value):
        if not self._checkKey(key):
            return
        if value is None:
            msg = '%s@%s%s%s\n' % (time, self._prefix, key, OP_TELLOLD)
        else:
            msg = '%s%s@%s%s%s%s\n' % (time, ttl,
                                       self._prefix, key, OP_TELL, value)
        self._queue.put(msg)

    def _handle_msg(self, _time, _ttlop, _ttl, _tsop, _key, _op, _value):
        pass


class MappingCacheForwarder(CacheForwarder):
    """Forwards cache updates to another cache, while remapping
    the device part of the key.
    """

    parameters = {
        'map': Param('Mapping for devices', type=dictof(str, str),
                     mandatory=True),
    }

    def _putChange(self, time, ttl, key, value):
        if not self._checkKey(key):
            return
        dev, slash, sub = key.partition('/')
        dev = self.map.get(dev, dev)
        if value is None:
            msg = '%s@%s%s%s\n' % (time, self._prefix, dev + slash + sub,
                                   OP_TELLOLD)
        else:
            msg = '%s%s@%s%s%s%s\n' % (time, ttl, self._prefix,
                                       dev + slash + sub, OP_TELL, value)
        self._queue.put(msg)


class WebhookForwarder(ForwarderBase, Device):
    """Forwards cache updates to a web service."""

    parameters = {
        'hook_url':      Param('Hook URL endpoint', type=str, mandatory=True),
        'prefix':        Param('Cache key prefix', type=str, mandatory=True),
        'http_mode':     Param('HTTP request mode', type=oneof('GET', 'POST'),
                               mandatory=True),
        'paramencoding': Param('Parameter encoding',
                               type=oneof('plain', 'json'), mandatory=True),
        'jsonname':      Param('JSON parameter name (used for GET requests)',
                               type=str, default='json'),
    }

    def doInit(self, mode):
        if requests is None:
            raise ConfigurationError(self, 'requests package is missing')
        self._prefix = self.prefix.strip('/')
        if self._prefix:
            self._prefix += '/'
        self._initFilters()
        self._queue = queue.Queue(1000)
        self._processor = createThread('webhookprocessor', self._processQueue)

    def _putChange(self, time, ttl, key, value):
        if not self._checkKey(key):
            return
        pdict = dict(time=time, ttl=ttl, key=self._prefix + key, value=value)
        retry = 2
        while retry:
            try:
                self._queue.put(pdict, False)
                break
            except queue.Full:
                self._queue.get()
                self._queue.task_done()
                retry -= 1

    def _webHookTask(self, pdict):
        try:
            if self.paramencoding == 'json':
                if self.http_mode == 'GET':
                    pdict = {self.jsonname: json.dumps(pdict)}
                    requests.get(self.hook_url, params=pdict, timeout=0.5)
                elif self.http_mode == 'POST':
                    requests.post(self.hook_url, json=pdict, timeout=0.5)
            else:
                if self.http_mode == 'GET':
                    requests.get(self.hook_url, params=pdict, timeout=0.5)
                elif self.http_mode == 'POST':
                    requests.post(self.hook_url, data=pdict, timeout=0.5)
        except Exception:
            self.log.warning('Execption during webhook call', exc=True)

    def _processQueue(self):
        while not self._stoprequest:
            item = self._queue.get()
            self._webHookTask(item)
            self._queue.task_done()


class Collector(CacheKeyFilter, BaseCacheClient):
    """The main service that enables cache update forwarding."""

    attached_devices = {
        'forwarders': Attach('The services to submit keys to',
                             ForwarderBase, multiple=True),
    }

    parameter_overrides = {
        'prefix': Override(mandatory=False, default='nicos/'),
    }

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        self._initFilters()
        for service in self._attached_forwarders:
            service._startWorker()

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if not key.startswith(self._prefix):
            return False
        key = key[len(self._prefix):]
        if not self._checkKey(key):
            return
        if op == OP_TELL:
            value = value or None
        elif op == OP_TELLOLD:
            value = None
        ttl = '+' + ttl if ttlop == '+' else ''
        for service in self._attached_forwarders:
            service._putChange(time, ttl, key, value)
