description = "Outside world data"
group = "lowlevel"

devices = dict(
    OutsideTemp = device('nicos.devices.entangle.Sensor',
        description = 'Outdoor air temperature',
        tangodevice = 'tango://ictrlfs.ictrl.frm2.tum.de:10000/frm2/meteo/temp',
    ),
    # meteo = device('nicos.devices.generic.DeviceAlias',
    #     devclass = 'nicos.devices.entangle.Sensor',
    #     alias = 'OutsideTemp',
    # ),
)

extended = dict(
    representative = 'OutsideTemp',
)
