# -*- coding: utf-8 -*-

__author__ = "Stefan Rainow <s.rainow@fz-juelich.de>"


description = "Outside world data"
group = "optional"


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
