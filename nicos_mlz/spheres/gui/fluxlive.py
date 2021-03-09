#  -*- coding: utf-8 -*-
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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# *****************************************************************************


from uuid import uuid1

import numpy

from nicos.clients.gui.panels.live import LiveDataPanel
from nicos.core.constants import LIVE


class FluxLivePanel(LiveDataPanel):
    def __init__(self, parent, client, options):
        LiveDataPanel.__init__(self, parent, client, options)

        self._datakey = options.get('key', None)
        client.cache.connect(self.on_client_cache)
        self.uuid = str(uuid1())

    def on_client_connected(self):
        LiveDataPanel.on_client_connected(self)

        if self._datakey is not None:
            data = self.client.getCacheKey(self._datakey)
            # if NICOS is restarting the cache might return None
            if data:
                self.displayData(0, *data[1])

    def on_client_cache(self, data):
        _time, key, op, value = data

        if key == self._datakey:
            value = eval(value)
            if op == '=':
                elastic, inelastic, direct = value
            elif op == '!':
                elastic = inelastic = direct = numpy.array([0]*16)

            self.displayData(_time, elastic, inelastic, direct)

    def displayData(self, time, elastic, inelastic, direct):
        newparams = dict(
            uid=self.uuid,
            time=time,
            det='flux',
            tag=LIVE,
            datadescs=[dict(
                dtype='<u8',
                shape=(16,),
                count=3)
            ],
        )

        self.on_client_livedata(newparams,
                                [numpy.concatenate((elastic,
                                                    inelastic,
                                                    direct))])
