# -*- coding: utf-8 -*-

description = "Outside world data"
group = "lowlevel"

devices = dict(
    ubahn = device('frm2.ubahn.UBahn',
                   description = 'Next subway departures',
                  ),
    meteo = device("jcns.meteo.MeteoStation",
                   description = "Outdoor air temperature",
                   query = "temperature/air",
                   location = "Garching",
                   unit = 'C',
                  ),
)
