description = 'Kompass setup for polarisation mode'

group = 'optional'

includes = ['diff']

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/kepco/'

devices = dict(
    coil_1 = device('nicos_mlz.panda.devices.guidefield.VectorCoil',
        description = 'Powersupply for horizontal field 1 at sample',
        tangodevice = tango_base + 'current1',
        abslimits = (-10, 10),
        orientation = (0.53, 0.53, 0.0),  # mT - calibrated 20/11/2013
        calibrationcurrent = 10,          # A
        lowlevel = True,
    ),
    coil_2 = device('nicos_mlz.panda.devices.guidefield.VectorCoil',
        description = 'Powersupply for horizontal field 2 at sample',
        tangodevice = tango_base + 'current2',
        abslimits = (-10, 10),
        orientation = (0.53, -0.53, 0.0),  # mT - calibrated 20/11/2013
        calibrationcurrent = 10,           # A
        lowlevel = True,
    ),
    coil_3 = device('nicos_mlz.panda.devices.guidefield.VectorCoil',
        description = 'Powersupply for vertical field at sample',
        tangodevice = tango_base + 'current3',
        abslimits = (-10, 10),
        orientation = (0, 0, 11.65),     # mT - calibrated 20/11/2013
        calibrationcurrent = 10,         # A
        lowlevel = True,
    ),
    gf = device('nicos_mlz.panda.devices.guidefield.GuideField',
        description = 'Vector field at sample location',
        alpha = 'alphastorage',
        coils = ['coil_1', 'coil_2', 'coil_3'],
        field = 10,    # mT
        mapping = {'off': None,
                   'perp':  ( 1., 0., 0.),
                   '-perp': (-1., 0., 0.),
                   'par':   ( 0., 1., 0.),
                   '-par':  ( 0.,-1., 0.),
                   'z':     ( 0., 0., 1.),
                   '-z':    ( 0., 0.,-1.),
                   'up':    ( 0., 0., 1.),
                   'down':  ( 0., 0.,-1.),
                   '0':     ( 0., 0., 0.)},
    ),
)
