description = 'RESEDA Motors'

group = 'lowlevel'

excludes = ['motors']

nethost = 'resedasrv'

devices = dict(
    m3 = device('devices.generic.VirtualMotor',
        description = 'Motor - Sample Table - Translation y',
        pollinterval = 5,
        maxage = 8,
        abslimits = (0, 100),
        unit = 'mm',
    ),
    m4 = device('devices.generic.VirtualMotor',
        description = 'Motor - Sample Table - Translation x',
        pollinterval = 5,
        maxage = 8,
        abslimits = (0, 100),
        unit = 'mm',
    ),
    m5 = device('devices.generic.VirtualMotor',
        description = 'Motor - Sample Table - Cradle in flight direction',
        pollinterval = 5,
        maxage = 8,
        abslimits = (0, 100),
        unit = 'deg',
    ),
    m6 = device('devices.generic.VirtualMotor',
        description = 'Motor - Sample Table - Cradle transversal to flight direction',
        pollinterval = 5,
        maxage = 8,
        abslimits = (0, 100),
        unit = 'deg',
    ),
    m7 = device('devices.generic.VirtualMotor',
        description = 'Motor - Sample Table - Rotation Omega',
        pollinterval = 5,
        maxage = 8,
        abslimits = (0, 100),
        unit = 'deg',
    ),
)
