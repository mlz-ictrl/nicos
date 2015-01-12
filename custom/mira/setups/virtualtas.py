description = 'fully virtual TAS setup'
group = 'basic'

includes = ['base']
excludes = ['tas']

modules = ['nicos.commands.tas']

devices = dict(
    Sample = device('devices.tas.TASSample'),

    mira   = device('devices.tas.TAS',
                    instrument = 'MIRA',
                    responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
                    axiscoupling = False,
                    psi360 = False,
                    cell = 'Sample',
                    phi = 'vphi',
                    psi = 'vom',
                    mono = 'vmono',
                    ana = 'vana',
                    alpha = None,
                    scatteringsense = (-1, 1, -1),
                   ),

    vom    = device('devices.generic.VirtualMotor',
                    abslimits = (-360, 360),
                    unit = 'deg',
                   ),

    vphi   = device('devices.generic.VirtualMotor',
                    abslimits = (0, 120),
                    unit = 'deg',
                   ),

    vmono  = device('devices.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'vmth',
                    twotheta = 'vmtt',
                    focush = None,
                    focusv = None,
                    abslimits = (0.1, 10),
                    dvalue = 3.325,
                   ),

    vana   = device('devices.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'vath',
                    twotheta = 'vatt',
                    focush = None,
                    focusv = None,
                    abslimits = (0.1, 10),
                    dvalue = 3.325,
                   ),

    vmth   = device('devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360),
                   ),

    vmtt   = device('devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360),
                   ),

    vath   = device('devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360),
                   ),

    vatt   = device('devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360),
                   ),

    ki     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'vmono',
                    tas = 'mira',
                    scanmode = 'CKI',
                   ),

    kf     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'vana',
                    tas = 'mira',
                    scanmode = 'CKF',
                   ),
)
