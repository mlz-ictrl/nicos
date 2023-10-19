description = 'Neutron Grating Interferometer at ICON'

group = 'optional'

excludes = ['ngi']

# Local private subnet
tango_host = 'phytron3.antareslab'

# At PSI -> needs to be in ICON network
# Phytron3 MAC: b8:27:eb:f3:31:b0
# tango_host = '172.28.77.82'

tango_base = f'tango://{tango_host}:10000/box/'

devices = dict(
    G0rz = device('nicos.devices.entangle.Motor',
        speed = 2.5,
        unit = 'deg',
        description = 'Rotation of G0 grating around beam direction',
        tangodevice = tango_base + 'phytron1/mot',
        abslimits = (-20, 20),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
    G1tx = device('nicos.devices.entangle.Motor',
        speed = 100,
        unit = 'um',
        description = 'Stepping of G1 perpendicular to the beam direction',
        tangodevice = tango_base + 'phytron4/mot',
        abslimits = (-12500, 12500),
        userlimits = (-12500, 12500),
        maxage = 5,
        pollinterval = 3,
        precision = 0.1,
    ),
    G1tz = device('nicos.devices.entangle.Motor',
        speed = 5,
        unit = 'mm',
        description = 'Translation of G1 parallel to the beam direction',
        tangodevice = tango_base + 'phytron3/mot',
        abslimits = (-80, 80),
        userlimits = (-80, 80),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
    G1rz = device('nicos.devices.entangle.Motor',
        speed = 5,
        unit = 'deg',
        description = 'Rotation of G1 around the beam axis',
        tangodevice = tango_base + 'phytron2/mot',
        abslimits = (-20, 20),
        userlimits = (-20, 20),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
)
