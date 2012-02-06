description = 'PANDA triple-axis setup'

includes = ['sampletable', 'ana', 'detector','system','panda_s7', 'manual', 'power']
# monoturm is included by panda_s7

#~ modules = ['nicos.commands.tas','nicos.panda.commands']
modules = ['nicos.commands.tas']

devices = dict(
    Sample = device('nicos.tas.TASSample'),

    panda = device('nicos.tas.TAS',
                    instrument = 'PANDA',
                    responsible = 'Astrid Schneidewind <astrid.schneidewind@frm2.tum.de>',
                    cell = 'Sample',
                    phi = 'stt',
                    psi = 'sth',
                    mono = 'mono',
                    ana = 'ana',
                    scatteringsense = (-1, 1, -1)),

    ki     = device('nicos.tas.Wavevector',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'panda',
                    scanmode = 'CKI',
                    abslimits = (1, 10)),

    kf     = device('nicos.tas.Wavevector',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'panda',
                    scanmode = 'CKF',
                    abslimits = (1, 10)),

    mono     = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'mth',
                      twotheta = 'mtt',
                      reltheta = True,
                      focush = None,
                      focusv = None,
                      abslimits = (0, 10),
                      dvalue = 3.355),

    ana     = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'ath',
                      twotheta = 'att',
                      focush = None,
                      focusv = None,
                      abslimits = (0, 10),
                      dvalue = 3.355),

)

startupcode = '''
#SetDetectors(det)
'''
