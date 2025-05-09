description = 'GALAXI motors setup'
group = 'optional'

tango_base = 'tango://phys.galaxi.jcns.fz-juelich.de:10000/galaxi/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    detz = device('nicos.devices.entangle.MotorAxis',
        description = 'PILATUS detector Z-axis.',
        tangodevice = s7_motor + 'detz',
        precision = 0.01,
    ),
    bssy = device('nicos.devices.entangle.MotorAxis',
        description = 'BSSY axis.',
        tangodevice = s7_motor + 'bssy',
        offset = 0,
        precision = 0.01,
    ),
    bspz = device('nicos.devices.entangle.MotorAxis',
        description = 'BSPZ axis.',
        tangodevice = s7_motor + 'bspz',
        offset = 0,
        precision = 0.01,
    ),
    bspy = device('nicos.devices.entangle.MotorAxis',
        description = 'BSPY axis.',
        tangodevice = s7_motor + 'bspy',
        offset = 0,
        precision = 0.01,
    ),
    pchi = device('nicos.devices.entangle.MotorAxis',
        description = 'Sample chi axis.',
        tangodevice = s7_motor + 'pchi',
        offset = 0,
        precision = 0.001,
    ),
    pom = device('nicos.devices.entangle.MotorAxis',
        description = 'Sample omega axis.',
        tangodevice = s7_motor + 'pom',
        offset = 0,
        precision = 0.001,
    ),
    pz = device('nicos.devices.entangle.MotorAxis',
        description = 'Sample Z-axis.',
        tangodevice = s7_motor + 'pz',
        offset = 0,
        precision = 0.01,
    ),
    py = device('nicos.devices.entangle.MotorAxis',
        description = 'Sample Y-axis.',
        tangodevice = s7_motor + 'py',
        offset = 0,
        precision = 0.01,
    ),
    prefz = device('nicos.devices.entangle.MotorAxis',
        description = 'Sample Z reference axis.',
        tangodevice = s7_motor + 'prefz',
        offset = 0,
        precision = 0.01,
    ),
)
