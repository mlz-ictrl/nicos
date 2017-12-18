description = 'The outside temperature on the campus'
group = 'lowlevel'

devices = dict(
    OutsideTemp = device('nicos.devices.tango.Sensor',
        description = 'Outdoor air temperature',
        tangodevice = 'tango://ictrlfs.ictrl.frm2:10000/frm2/meteo/temp',
    ),
)
