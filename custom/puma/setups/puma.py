description = 'PUMA triple-axis setup'

includes = ['virtualtas', 'sampletable', 'power', 'detector', 'monochromator', 'analyser', 'ios']

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
                      focush = 'mfhpg',
                      focusv = 'mfvpg',
                      hfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901],
                      vfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901],
                      abslimits = (1, 6),
                      dvalue = 3.355),

    ana     = device('devices.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'ath',
                      twotheta = 'att',
                      reltheta = True,
                      focush = 'afpg',
                      focusv = None,
                      hfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901],
                      abslimits = (1, 5),
                      dvalue = 3.355),
)

startupcode = '''
SetDetectors(det)
'''
