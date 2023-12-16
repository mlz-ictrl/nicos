description = 'The outside temperature on the campus'
group = 'lowlevel'

devices = dict(
    OutsideTemp = device('nicos.devices.entangle.Sensor',
        description = 'Outdoor air temperature',
        tangodevice = 'tango://ictrlfs.ictrl.frm2.tum.de:10000/frm2/meteo/temp',
    ),
)
