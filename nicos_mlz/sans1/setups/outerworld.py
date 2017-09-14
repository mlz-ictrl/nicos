description = "Outside world data"
group = "lowlevel"

devices = dict(
    meteo = device('nicos.devices.tango.Sensor',
                   description = 'Outdoor air temperature',
                   tangodevice = 'tango://ictrlfs.ictrl.frm2:10000/frm2/meteo/temp',
                  ),
)
