description = 'Neutron Grating Interferometer'

group = 'optional'

excludes = ['ngi', 'ngi_ill', 'neutrosense', 'ngi_icon']

tango_host = 'phytron3.antareslab'

tango_base = f'tango://{tango_host}:10000/box/'

devices = dict(
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
        speed = 1.5,
        unit = 'mm',
        description = 'Translation of G1 parallel to the beam direction',
        tangodevice = tango_base + 'phytron3/mot',
        abslimits = (-10, 10),
        userlimits = (-10, 10),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
    G1rz = device('nicos.devices.entangle.Motor',
        speed = 0.2,
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
