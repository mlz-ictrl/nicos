# -*- coding: utf-8 -*-

description = "Outside world data"
group = "lowlevel"

devices = dict(
    ubahn = device('nicos_mlz.devices.mvg.MVG',
        description = 'Next subway departures',
        tangodevice='tango://ictrlfs.ictrl.frm2.tum.de:10000/mvg/U6/departures',
        limit =3 ,
    ),
    meteo = device('nicos.devices.entangle.Sensor',
        description = 'Outdoor air temperature',
        tangodevice = 'tango://ictrlfs.ictrl.frm2:10000/frm2/meteo/temp',
    ),
)
