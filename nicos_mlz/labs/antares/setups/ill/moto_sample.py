description = 'Neutron Grating Interferometer'

group = 'optional'

excludes = ['ngi', 'ngi_ill', 'neutrosense', 'ngi_icon', 'ngi_ill_g1', 'sample_stage']

tango_host = 'phytron2.antareslab'

tango_base = f'tango://{tango_host}:10000/box/'

devices = dict(
    G1tx = device('nicos.devices.entangle.Motor',
        speed = 100,
        unit = 'um',
        description = 'Stepping of G1 perpendicular to the beam direction',
       tangodevice = tango_base + 'phytron1/mot',
        abslimits = (-12500, 12500),
        userlimits = (-12500, 12500),
        maxage = 5,
        pollinterval = 3,
        precision = 0.1,
    ),
    stx = device('nicos.devices.entangle.Motor',
        speed = 3,
        unit = 'mm',
        description = 'Translation of the sample perpendicular to the beam direction',
        tangodevice = tango_base + 'phytron2/mot',
        abslimits = (-1, 100),
        userlimits = (0, 100),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
    stz = device('nicos.devices.entangle.Motor',
        speed = 2,
        unit = 'mm',
        description = 'Translation of the sample parallel to the beam direction',
        tangodevice = tango_base + 'phytron3/mot',
        abslimits = (0, 295),
        userlimits = (0, 295),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
)
