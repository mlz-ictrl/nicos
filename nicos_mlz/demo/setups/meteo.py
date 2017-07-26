# -*- coding: utf-8 -*-

_TEMP_AIR      = "temperature/air"
_TEMP_WET_BULB = "temperature/wet_bulb"
_DEWPOINT      = "dewpoint"
_HUMIDITY      = "humidity"
_WIND_SPEED    = "wind/speed"

description = "weather measuring stations provided by LMU"
group = "optional"

devices = dict(
    T_out    = device("nicos_mlz.jcns.devices.meteo.MeteoStation",
                      description = "Outdoor air temperature",
                      query = _TEMP_AIR,
                      location = "Garching",
                      unit = 'C',
                     ),
    T_out_5  = device("nicos_mlz.jcns.devices.meteo.MeteoStation",
                      description = "T_out (Outdoor air temperature) at 5m height",
                      query = _TEMP_AIR,
                      height = 5.0,
                      unit = 'C',
                     ),
    phi_air  = device("nicos_mlz.jcns.devices.meteo.MeteoStation",
                      description = "humidity",
                      query = _HUMIDITY,
                      location = "Garching",
                      fmtstr = "%d",
                      unit = '%',
                     ),
    v_wind   = device("nicos_mlz.jcns.devices.meteo.MeteoStation",
                      description = "wind speed",
                      query = _WIND_SPEED,
                      unit = "m/s",
                     ),
)
