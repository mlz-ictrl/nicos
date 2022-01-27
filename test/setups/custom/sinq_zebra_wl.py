name = 'ZEBRA wavelength test'
description = 'Devices for the testing the wavelength device at ZEBRA'

includes = ['generic']

devices = dict(
    mexz = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy monochromator lift',
        unit = 'mm',
        abslimits = (0, 550),
    ),
    moml = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy omega rotation',
        unit = 'deg',
        abslimits = (-160, 160),
    ),
    mcvl = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy monochromator curvature',
        unit = 'mm',
        abslimits = (0, 10),
    ),
    momu = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy omega rotation',
        unit = 'deg',
        abslimits = (-160, 160),
    ),
    mcvu = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy curvaturw',
        unit = 'mm',
        abslimits = (0, 300),
    ),
    pg = device('nicos.devices.generic.ManualSwitch',
        desription = 'Virtual PG filter',
        states = ['In', 'Out']
    ),
    wl = device('nicos_sinq.zebra.devices.zebrawl.ZebraWavelength',
        description = 'Zebra Wavelength test',
        unit = 'A-1',
        mexz = 'mexz',
        pg = 'pg',
        moml = 'moml',
        mcvl = 'mcvl',
        momu = 'momu',
        mcvu = 'mcvu'
    ),
)
