description = "Outside world data"
group = "lowlevel"

devices = dict(
    ubahn = device('nicos_mlz.devices.mvg.MVG',
        description = 'Next subway departures',
        tangodevice='tango://ictrlfs.ictrl.frm2.tum.de:10000/mvg/U6/departures',
        limit =3 ,
    ),
    meteo = device('nicos.devices.generic.VirtualCoder',
        description = 'Outdoor air temperature',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-30, 40),
            curvalue = 20,
            ramp = 0.1,
            unit = 'degC',
        ),
    ),
)
