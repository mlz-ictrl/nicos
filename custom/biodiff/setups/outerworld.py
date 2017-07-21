# -*- coding: utf-8 -*-

description = "Outside world data"
group = "lowlevel"

devices = dict(
    ubahn = device('nicos_mlz.frm2.devices.ubahn.UBahn',
                   description = 'Next subway departures',
                  ),
    meteo = device('nicos_mlz.jcns.devices.meteo.MeteoStation',
                   description = 'Outdoor air temperature',
                   query = 'temperature/air',
                   location = 'Garching',
                   unit = 'C',
                  ),
)
