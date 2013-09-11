description = 'PANDA triple-axis setup'

group = 'basic'

includes = ['system', 'sampletable', 'ana', 'detector', 'panda_s7', 'manual', 'alias_sth']
# monoturm is included by panda_s7

#~ modules = ['nicos.commands.tas','nicos.panda.commands']
modules = ['nicos.commands.tas']

devices = dict(
    alphastorage = device('panda.guidefield.AlphaStorage',
                           description = 'Virtual device for handling \alpha changes',
                           abslimits = (-360, 360),
                           unit = 'deg',
                           lowlevel = True,
    ),
    panda = device('devices.tas.TAS',
                    instrument = 'PANDA',
                    responsible = 'Astrid Schneidewind <astrid.schneidewind@frm2.tum.de>',
                    cell = 'Sample',
                    phi = 'stt',
                    psi = 'sth',
                    mono = 'mono',
                    ana = 'ana',
                    alpha = 'alphastorage',
                    scatteringsense = (-1, 1, -1),
                    energytransferunit ='meV',
#                    countloopdelay = 0.2,
    ),
    ki    = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'panda',
                    scanmode = 'CKI',
    ),
    kf    = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'panda',
                    scanmode = 'CKF',
    ),
    mono  = device('devices.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'mth',
                    twotheta = 'mtt',
                    reltheta = True,
                    focush = 'mfh',
                    focusv = 'mfv',
                    hfocuspars = [294.28075, -5.3644, -0.1503],
                    vfocuspars = [418.22, -326.12, 116.331, -19.0842, 1.17283],
                    abslimits = (1, 10),
                    dvalue = 3.355,
    ),
    ana   = device('devices.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'ath',
                    twotheta = 'att',
                    focush = 'afh',
                    focusv = None,
                    abslimits = (1, 10),
                    hfocuspars = [44.8615, 4.64632, 2.22023],
                    dvalue = 3.355,
    ),
    sth_virtual_dummy = device('devices.generic.VirtualMotor',
                                unit = 'deg',
                                abslimits = (0, 360),
                                userlimits = (5, 355),
                                description = 'Virtual device to startup the TAS-Device, DONT USE !',
                                lowlevel = True,
                                fixed = 'DO NOT USE THIS DUMMY DEVICE! please set sth.alias to another device.',
                                fixedby = ('NICOS', 99),
    ),
)

startupcode = '''
#~ sth.alias = 'sth_virtual_dummy'
SetDetectors(det)
'''
