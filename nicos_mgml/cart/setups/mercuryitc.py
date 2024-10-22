description = 'Triton MercuryITC controller'
group = 'optional'

tango_base = 'tango://localhost:10000/triton/'

devices = dict(
    T_ITC_MC = device('nicos.devices.entangle.Sensor',
        description = 'Mixing Chamber',
        tangodevice = tango_base + 'itc/mb1',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_ITC_Still = device('nicos.devices.entangle.Sensor',
        description = 'Still thermometer',
        tangodevice = tango_base + 'itc/db6',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_ITC_Pt2 = device('nicos.devices.entangle.Sensor',
        description = 'Pt2 thermometer',
        tangodevice = tango_base + 'itc/db7',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_ITC_Pt1 = device('nicos.devices.entangle.Sensor',
        description = 'Pt1 thermometer',
        tangodevice = tango_base + 'itc/db8',
        pollinterval = 0.7,
        maxage = 2,
    ),
)

