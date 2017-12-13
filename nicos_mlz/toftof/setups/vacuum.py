description = 'chopper vacuum readout'

group = 'lowlevel'

includes = []

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    vac0 = device('nicos.devices.taco.io.AnalogInput',
        description = 'Vacuum sensor in chopper vessel 1',
        tacodevice = '//%s/toftof/vacuum/sens1' % nethost,
        pollinterval = 10,
        maxage = 12,
        unit = 'mbar',
    ),
    vac1 = device('nicos.devices.taco.io.AnalogInput',
        description = 'Vacuum sensor in chopper vessel 2',
        tacodevice = '//%s/toftof/vacuum/sens2' % nethost,
        pollinterval = 10,
        maxage = 12,
        unit = 'mbar',
    ),
    vac2 = device('nicos.devices.taco.io.AnalogInput',
        description = 'Vacuum sensor in chopper vessel 3',
        tacodevice = '//%s/toftof/vacuum/sens3' % nethost,
        pollinterval = 10,
        maxage = 12,
        unit = 'mbar',
    ),
    vac3 = device('nicos.devices.taco.io.AnalogInput',
        description = 'Vacuum sensor in chopper vessel 4',
        tacodevice = '//%s/toftof/vacuum/sens4' % nethost,
        pollinterval = 10,
        maxage = 12,
        unit = 'mbar',
    ),
)
