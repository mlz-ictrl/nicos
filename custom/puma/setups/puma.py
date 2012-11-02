description = 'PANDA triple-axis setup'

includes = ['virtualtas', 'sampletable', 'analyser', 'power', 'detector',
            'lengths']

modules = ['nicos.commands.tas']

devices = dict(
    Sample = device('devices.tas.TASSample'),

    puma   = device('devices.tas.TAS',
                    instrument = 'PUMA',
                    responsible = 'O. Sobolev',
                    cell = 'Sample',
                    phi = 'phi',
                    psi = 'psi',
                    mono = 'mono',
                    ana = 'ana',
                    alpha = None,
                    scatteringsense = (-1, 1, -1),
                    energytransferunit = 'meV',
                    axiscoupling = True),

    ki     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'puma',
                    scanmode = 'CKI',
                    abslimits = (1, 5)),

    kf     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'puma',
                    scanmode = 'CKF',
                    abslimits = (1, 5)),

    mono     = device('devices.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'mth',
                      twotheta = 'mtt',
                      reltheta = True,
                      focush = None,
                      focusv = None,
                      abslimits = (1, 5),
                      dvalue = 3.355),

    ana     = device('devices.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'ath_raw',
                      twotheta = 'att',
                      reltheta = -1,
                      focush = 'afh',
                      focusv = None,
                      abslimits = (1, 5),
                      dvalue = 3.355),

)

startupcode = '''
SetDetectors(det)
'''
