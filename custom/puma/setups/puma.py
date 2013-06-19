description = 'PUMA triple-axis setup'

includes = ['sampletable', 'detector', 'monochromator', 'analyser', 'ios', 'lengths', 'reactor']

modules = ['nicos.commands.tas']

group = 'basic'

devices = dict(
    Sample = device('devices.tas.TASSample'),

    #~ puma   = device('devices.tas.TAS',
    puma   = device('puma.spectro.PUMA',
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
                    abslimits = (1, 10),
# Cu220                   abslimits = (2, 10),
                    ),

    kf     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'puma',
                    scanmode = 'CKF'
                    ),

    Ei     = device('devices.tas.Energy',
                    unit = 'meV',
                    base = 'mono',
                    tas = 'puma',
                    scanmode = 'CKI'
                    ),

    Ef     = device('devices.tas.Energy',
                    unit = 'meV',
                    base = 'ana',
                    tas = 'puma',
                    scanmode = 'CKF',
                    ),

    mono     = device('devices.generic.DeviceAlias',
                      alias = None,
                      devclass = 'devices.tas.Monochromator',
                      ),

    mono_pg002     = device('devices.tas.Monochromator',
                      description = 'PG-002 monochromator',
                      order = 1,
                      unit = 'A-1',
                      theta = 'mth',
                      twotheta = 'mtt',
                      reltheta = True,
                      focush = 'mfhpg',
                      focusv = 'mfvpg',
                      hfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901],
                      vfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901], # focus value should equal mth (for arcane reasons...)
                      abslimits = (1, 6),
                      dvalue = 3.355,
                      ),

    mono_pg004     = device('devices.tas.Monochromator',
                      description = 'PG-002 used as 004 monochromator',
                      order = 2,
                      unit = 'A-1',
                      theta = 'mth',
                      twotheta = 'mtt',
                      reltheta = True,
                      focush = 'mfhpg',
                      focusv = 'mfvpg',
#                      focush = 'mfhcu',
#                      focusv = 'mfvcu',
                      hfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901],
                      vfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901],
#                      hfocuspars = [1.34841,15.207,12.41842,-8.01148,2.13633],
#                      vfocuspars = [1.34841,15.207,12.41842,-8.01148,2.13633],
#                      abslimits = (1, 6),
                      abslimits = (1, 10),
                      dvalue = 3.355,
#                      dvalue = 1.278,
                      ),

    ana     = device('devices.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'ath',
                      twotheta = 'att',
                      reltheta = True,
                      focush = 'afpg',
                      focusv = None,
                      hfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901],
                      abslimits = (1, 5),
                      dvalue = 3.355,
                      ),
)

startupcode = '''
mono.alias = mono_pg002
'''
