# -*- coding: utf-8 -*-

description = "Outside world data"
group = "lowlevel"

devices = dict(
    ubahn = device('nicos_mlz.frm2.devices.ubahn.UBahn',
        description = 'Next subway departures',
    ),
    meteo = device('nicos.devices.tango.Sensor',
        description = 'Outdoor air temperature',
        tangodevice = 'tango://ictrlfs.ictrl.frm2:10000/frm2/meteo/temp',
    ),
)
