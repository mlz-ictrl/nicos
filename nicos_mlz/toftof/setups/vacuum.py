description = 'chopper vacuum readout'

group = 'lowlevel'

tango_host = 'tango://tofhw.toftof.frm2:10000/toftof/vacuum/'

devices = dict(
    vac0 = device('nicos.devices.tango.Sensor',
        description = 'Vacuum sensor in chopper vessel 1',
        tangodevice = tango_host + 'sens1',
        pollinterval = 10,
        maxage = 12,
    ),
    vac1 = device('nicos.devices.tango.Sensor',
        description = 'Vacuum sensor in chopper vessel 2',
        tangodevice = tango_host + 'sens2',
        pollinterval = 10,
        maxage = 12,
    ),
    vac2 = device('nicos.devices.tango.Sensor',
        description = 'Vacuum sensor in chopper vessel 3',
        tangodevice = tango_host + 'sens3',
        pollinterval = 10,
        maxage = 12,
    ),
    vac3 = device('nicos.devices.tango.Sensor',
        description = 'Vacuum sensor in chopper vessel 4',
        tangodevice = tango_host + 'sens4',
        pollinterval = 10,
        maxage = 12,
    ),
)
