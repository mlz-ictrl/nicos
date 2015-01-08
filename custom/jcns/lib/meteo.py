# -*- coding: utf-8 -*-
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

# standard library
from nicos.core.errors import NicosError
# third party
try:
    _thirdparty_available = True
    import requests
except ImportError as e:
    _thirdparty_available = False
    _import_error = e
# local library
from nicos.core.device import Readable, HasOffset
from nicos.core.params import Param, oneof, Override
import nicos.core.status as status

__author__ = "Christian Felder <c.felder@fz-juelich.de>"
__date__ = "2013-11-05"
__version__ = "0.1.1"

_REST_URL = "http://jcnswww.jcns.frm2/meteo"

class MeteoStation(Readable, HasOffset):

    TEMP_AIR = "temperature/air"
    TEMP_WET_BULB = "temperature/wet_bulb"
    DEWPOINT = "dewpoint"
    HUMIDITY = "humidity"
    WIND_SPEED = "wind/speed"

    _MAP_REST = { TEMP_AIR: "temperature_air",
                  TEMP_WET_BULB: "temperature_wet_bulb",
                  DEWPOINT: "dewpoint", HUMIDITY: "humidity",
                  WIND_SPEED: "speed_wind" }

    parameters = {
                  "location": Param("Meteo Station location", type=str,
                                    settable=True, mandatory=False,
                                    default="Garching"),
                  "query": Param("Meteo Station query parameter",
                                 type=oneof(TEMP_AIR,
                                            TEMP_WET_BULB,
                                            DEWPOINT,
                                            HUMIDITY,
                                            WIND_SPEED),
                                 settable=False, mandatory=True),
                  "height": Param("Height of Measurement", type=float,
                                  settable=True, mandatory=False, default=2.)
                  }

    parameter_overrides = { "fmtstr": Override(default="%.1f"),
                            "maxage": Override(default=120),
                            "pollinterval": Override(default=60) }

    def doInit(self, mode):
        self._status = status.OK, ''

    def _query(self):
        result = None
        if _thirdparty_available:
            res = requests.get(_REST_URL + '/' + self.location + '/' +
                               self.query + "/by-height/%.1f" % self.height)
            self.log.debug("REST-statuscode: %d" % res.status_code)
            if res.status_code == 200:
                result = res.json()[MeteoStation._MAP_REST[self.query]]["value"]
                self._status = status.OK, ''
            else:
                errmsg = ("MeteoMunich, RESTful Webservice HTTPError %d"
                          % res.status_code)
                self._status = (status.ERROR, errmsg)
                raise NicosError(self, errmsg)
        return result

    def doRead(self, maxage=0):
        self.log.debug("maxage=%d" % maxage)
        result = self._query()
        if result is not None:
            result += self.offset
        return result

    def doStatus(self, maxage=0):
        if not _thirdparty_available:
            self._status = status.ERROR, str(_import_error)
        return self._status

    def doWriteUnit(self, value):
        self.log.debug("unit=%s" % str(value))
        if value == 'K':
            self.offset = 273.15
        else:
            self.offset = 0
