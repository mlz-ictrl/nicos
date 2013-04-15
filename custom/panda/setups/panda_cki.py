description = 'PANDA triple-axis setup for fixed CKI mode (mtt broken)'

group = 'basic'

includes = ['sampletable', 'ana', 'detector','system','monoturm','manual']
# monoturm is included by panda_s7

#~ modules = ['nicos.commands.tas','nicos.panda.commands']
modules = ['nicos.commands.tas']

devices = dict(
    Sample = device('devices.tas.TASSample'),

    panda = device('devices.tas.TAS',
                    instrument = 'PANDA',
                    responsible = 'Astrid Schneidewind <astrid.schneidewind@frm2.tum.de>',
                    cell = 'Sample',
                    phi = 'stt',
                    psi = 'sth',
                    mono = 'mono',
                    ana = 'ana',
                    alpha = None,
                    scatteringsense = (-1, 1, -1),
                    energytransferunit ='meV',
                    countloopdelay = 0.2,
                    maxage = 1e-20, # to force a recalculation on every readout
    ),

    ki     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'panda',
                    scanmode = 'CKI'),

    kf     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'panda',
                    scanmode = 'CKF'),

    mono     = device('devices.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'mth',
                      twotheta = 'mtt',
                      reltheta = True,
                      focush = 'mfh',
                      focusv = 'mfv',
                      hfocuspars = [294.28075, -5.3644, -0.1503],
                      vfocuspars = [418.22, -326.12, 116.331, -19.0842, 1.17283],
                      abslimits = (1, 10),
                      dvalue = 3.355),

    ana     = device('devices.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'ath',
                      twotheta = 'att',
                      focush = 'afh',
                      focusv = None,
                      abslimits = (1, 10),
                      hfocuspars = [44.8615, 4.64632, 2.22023],
                      dvalue = 3.355),

    sth_virtual_dummy = device('devices.generic.VirtualMotor',
        unit='blubb',
        abslimits=(0,360),
        userlimits=(5,355),
        description='Virtual device to startup the TAS-Device',
        lowlevel=True,
    ),

    sth = device('devices.generic.DeviceAlias',
            alias='sth_virtual_dummy',
            description='Alias to currently used sth-device',
    ),

    mtt_virtual_dummy = device('devices.generic.VirtualMotor',
        unit='deg',
        abslimits=(-360,360),
        userlimits=(-355,355),
        description='Virtual device to startup the TAS-Device',
        lowlevel=True,
    ),

    mtt=device('devices.generic.Axis',
            unit='deg',
            abslimits=(-132, -20),
            coder='mtt_enc',
            motor='mtt_virtual_dummy',
            fixed='fixed',
            obs=['mtt_enc'],
            precision=0.01,
            offset = 0.1065015,
            description='QndH for CKI-Mode with broken mtt',
    ),

)

startupcode = '''
SetDetectors(det)
'''
