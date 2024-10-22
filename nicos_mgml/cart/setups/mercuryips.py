description = 'Triton MercuryIPS controller'
group = 'optional'

tango_base = 'tango://localhost:10000/triton/'

devices = dict(
    Bx = device('nicos.devices.entangle.Actuator',
        description = 'Field along x axis in 611 vector magnet',
        tangodevice = tango_base + 'ips/bx',
        pollinterval = 0.7,
        maxage = 2,
    ),
    By = device('nicos.devices.entangle.Actuator',
        description = 'Field along y axis in 611 vector magnet',
        tangodevice = tango_base + 'ips/by',
        pollinterval = 0.7,
        maxage = 2,
    ),
    Bz = device('nicos.devices.entangle.Actuator',
        description = 'Field along z axis in 611 vector magnet',
        tangodevice = tango_base + 'ips/bz',
        pollinterval = 0.7,
        maxage = 2,
    ),
    Bfake = device('nicos.devices.entangle.AnalogOutput',
        description = 'Manual device for transfering any device to MultiVu',
        tangodevice = tango_base + 'ips/bfake',
        pollinterval = 0.7,
        maxage = 2,
    ),
)

