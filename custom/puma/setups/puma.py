description = 'PANDA triple-axis setup'

includes = ['virtualtas', 'sampletable', 'power', 'detector']

modules = ['nicos.commands.tas']

devices = dict(
    Sample = device('nicos.tas.TASSample'),

    puma   = device('nicos.tas.TAS',
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

    ki     = device('nicos.tas.Wavevector',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'puma',
                    scanmode = 'CKI',
                    abslimits = (1, 5)),

    kf     = device('nicos.tas.Wavevector',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'puma',
                    scanmode = 'CKF',
                    abslimits = (1, 5)),

    mono     = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'mth',
                      twotheta = 'mtt',
                      reltheta = True,
                      focush = None,
                      focusv = None,
                      abslimits = (1, 5),
                      dvalue = 3.355),

    ana     = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'ath',
                      twotheta = 'att',
                      focush = None,
                      focusv = None,
                      abslimits = (1, 5),
                      dvalue = 3.355),

)

startupcode = '''
SetDetectors(det)
'''
