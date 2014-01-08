description = 'fully virtual TAS setup'
group = 'basic'

includes = ['base']

modules = ['nicos.commands.tas']

devices = dict(
    Sample = device('devices.tas.TASSample'),

    mira   = device('devices.tas.TAS',
                    instrument = 'MIRA',
                    responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
                    axiscoupling = False,
                    psi360 = False,
                    cell = 'Sample',
                    phi = 'phi',
                    psi = 'om',
                    mono = 'mono',
                    ana = 'ana',
                    alpha = None,
                    scatteringsense = (-1, 1, -1)),

    mono   = device('devices.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'vmth',
                    twotheta = 'vmtt',
                    focush = None,
                    focusv = None,
                    abslimits = (0.1, 10),
                    dvalue = 3.325),

    ana    = device('devices.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'vath',
                    twotheta = 'vatt',
                    focush = None,
                    focusv = None,
                    abslimits = (0.1, 10),
                    dvalue = 3.325),

    vmth   = device('devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360)),

    vmtt   = device('devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360)),

    vath   = device('devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360)),

    vatt   = device('devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360)),

    ki     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'mira',
                    scanmode = 'CKI'),

    kf     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'mira',
                    scanmode = 'CKF'),
)
