#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""The NICOS version info pushing daemon."""

from datetime import datetime
try:
    # recommended
    import simplejson as json
except ImportError:
    # fallback
    import json

from nicos import nicos_version, custom_version, config
from nicos.core import Param, Override, none_or
from nicos.devices.cacheclient import BaseCacheClient
from nicos.protocols.cache import OP_TELL, OP_TELLOLD, cache_load
from nicos.utils import getfqdn
from nicos.pycompat import urllib

TIME_FMT = '%Y-%m-%d %H:%M:%S'


class PushVersionInfo(BaseCacheClient):
    r"""Pushes the version info to a storage service.

    The version infos are pushed as a JSON array.  The content is not
    defined, but normally the following keys can be available::

      instrument
      host
      nicos_root
      nicos_version
      custom_version
      service [opt.]
      base_version  \  these two are only posted
      base_host     /  from this service
    """

    parameters = {
        'update_uri': Param('URI to send version information to, or None to '
                            'disable. Version info is directly appended to '
                            'the URI, encoded as a query parameter.',
                            type=none_or(str), mandatory=True),
        'infokey':    Param('URI parameter key for the info dict', type=str,
                            mandatory=True),
    }

    parameter_overrides = {
        'prefix':     Override(mandatory=False, default='sysinfo/'),
    }

    def _connect_action(self):
        BaseCacheClient._connect_action(self)
        self.sendUpdate()

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if not key.startswith(self.prefix):
            return
        if op in [OP_TELL, OP_TELLOLD]:
            self.processSysinfo(key, value, time, tell=False)

    def processSysinfo(self, key, value, time, tell):
        if not tell:
            infodict = dict(cache_load(value))
            if time:
                dt = datetime.fromtimestamp(float(time))
                infodict['time'] = dt.strftime(TIME_FMT)
            self.sendUpdate(infodict)

    def getDaemonInfo(self):
        instrument = config.instrument
        base_host = getfqdn()

        # collect data to send, data should be strings!
        infodict = dict(
            time=datetime.now().strftime(TIME_FMT),
            instrument=instrument,
            base_host=base_host,
            base_version=nicos_version,
            nicos_root=config.nicos_root,
            custom_path=config.custom_path,
            custom_version=custom_version,
        )
        return infodict

    def sendUpdate(self, infodict=None, time=None):
        # make json
        if not self.update_uri:
            return
        if infodict is None:
            infodict = self.getDaemonInfo()

        paramdict = {self.infokey: json.dumps(infodict)}
        update_string = self.update_uri + urllib.parse.urlencode(paramdict)

        try:
            urllib.request.urlopen(update_string)
            self.log.debug('update sent successfully for %s' %
                           infodict.get('service', 'base'))
        except Exception:
            self.log.debug('cannot send version information! (tried:\n%r\n)' %
                           update_string, exc=True)
