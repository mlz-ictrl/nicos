description = 'Neutron Grating Interferometer at ICON'

group = 'optional'

excludes = ['ngi', 'neutrosense', ]

# Local private subnet

tango_host = 'phytron3.antareslab'

# At PSI -> needs to be in ICON network
# Phytron3 MAC: b8:27:eb:f3:31:b0
# tango_host = '172.28.77.82'

tango_base = f'tango://{tango_host}:10000/box/'

devices = dict(
    stx = device('nicos.devices.entangle.Motor',
        speed = 2.5,
        unit = 'mm',
        description = 'Sample translation parallel to the beam direction',
        tangodevice = tango_base + 'phytron6/mot',
        abslimits = (0, 100),
        userlimits = (0, 100),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
    srz = device('nicos.devices.entangle.Motor',
        speed = 5,
        unit = 'deg',
        description = 'Sample translation parallel to the beam direction',
        tangodevice = tango_base + 'phytron8/mot',
        abslimits = (-999, 999),
        userlimits = (-999, 999),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
    # Huber 400mm
    stz = device('nicos.devices.entangle.Motor',
        speed = 2.5,
        unit = 'mm',
        description = 'Sample translation parallel to the beam direction',
        tangodevice = tango_base + 'phytron7/mot',
        abslimits = (0, 400),
        userlimits = (0, 400),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
    # OWIS Stage
    # stz = device('nicos.devices.entangle.Motor',
    #     speed = 5,
    #     unit = 'mm',
    #     description = 'Sample translation parallel to the beam direction',
    #     tangodevice = tango_base + 'phytron8/mot',
    #     abslimits = (0, 295),
    #     userlimits = (0, 295),
    #     maxage = 5,
    #     pollinterval = 3,
    #     precision = 0.001,
    # ),
)
