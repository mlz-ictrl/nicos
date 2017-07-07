description = 'fully virtual TAS setup'
group = 'basic'

includes = ['base', 'sample']
excludes = ['tas']

modules = ['commands.tas']

devices = dict(
    Sample = device('nicos.devices.tas.TASSample',
                    description = 'sample object',
                   ),

    mira   = device('nicos.devices.tas.TAS',
                    description = 'instrument, moves in HKL space',
                    instrument = 'MIRA',
                    responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
                    axiscoupling = False,
                    psi360 = False,
                    cell = 'Sample',
                    phi = 'vstt',
                    psi = 'vsth',
                    mono = 'vmono',
                    ana = 'vana',
                    alpha = None,
                    scatteringsense = (-1, 1, -1),
                   ),

    vsth   = device('nicos.devices.generic.VirtualMotor',
                    description = 'virtual sample theta',
                    abslimits = (-360, 360),
                    unit = 'deg',
                   ),

    vstt   = device('nicos.devices.generic.VirtualMotor',
                    description = 'virtual sample two-theta',
                    abslimits = (0, 120),
                    unit = 'deg',
                   ),

    vmono  = device('nicos.devices.tas.Monochromator',
                    description = 'virtual monochromator',
                    unit = 'A-1',
                    theta = 'vmth',
                    twotheta = 'vmtt',
                    focush = None,
                    focusv = None,
                    abslimits = (0.1, 10),
                    dvalue = 3.325,
                    crystalside = -1,
                   ),

    vana   = device('nicos.devices.tas.Monochromator',
                    description = 'virtual analyzer',
                    unit = 'A-1',
                    theta = 'vath',
                    twotheta = 'vatt',
                    focush = None,
                    focusv = None,
                    abslimits = (0.1, 10),
                    dvalue = 3.325,
                    crystalside = -1,
                   ),

    vmth   = device('nicos.devices.generic.VirtualMotor',
                    description = 'virtual monochromator theta',
                    unit = 'deg',
                    abslimits = (-360, 360),
                   ),

    vmtt   = device('nicos.devices.generic.VirtualMotor',
                    description = 'virtual monochromator two-theta',
                    unit = 'deg',
                    abslimits = (-360, 360),
                   ),

    vath   = device('nicos.devices.generic.VirtualMotor',
                    description = 'virtual analysator theta',
                    unit = 'deg',
                    abslimits = (-360, 360),
                   ),

    vatt   = device('nicos.devices.generic.VirtualMotor',
                    description = 'virtual analysator two-theta',
                    unit = 'deg',
                    abslimits = (-360, 360),
                   ),

    ki     = device('nicos.devices.tas.Wavevector',
                    description = 'incoming wavevector, also sets constant-ki mode when moved',
                    unit = 'A-1',
                    base = 'vmono',
                    tas = 'mira',
                    scanmode = 'CKI',
                   ),

    kf     = device('nicos.devices.tas.Wavevector',
                    description = 'outgoing wavevector, also sets constant-kf mode when moved',
                    unit = 'A-1',
                    base = 'vana',
                    tas = 'mira',
                    scanmode = 'CKF',
                   ),
)
