description = 'Polariser devices in the SINQ AMOR.'

display_order = 30

pvprefix = 'SQ:AMOR:mcu1:'

devices = dict(
    pz1 = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Polariser Z-translation 1',
        motorpv = pvprefix + 'pz1',
        errormsgpv = pvprefix + 'pz1-MsgTxt',
        can_disable = True,
        visibility = ('metadata', 'namespace'),
    ),
    pz2 = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Polariser Z-translation 2',
        motorpv = pvprefix + 'pz2',
        errormsgpv = pvprefix + 'pz2-MsgTxt',
        can_disable = True,
        visibility = ('metadata', 'namespace'),
    ),
    polarisation = device('nicos.devices.generic.switcher.MultiSwitcher',
        description = 'move polariser in or out of the beam',
        moveables = ['pz1', 'pz2', 'spinflipper_amp'],
        mapping = {
            'on': [13.5, 12.0, 0.],
            'off': [91.3, 90.8, 0.],
        },
        precision = [None],
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    spinflipper_amp = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Spin Flipper Amplitude',
        writepv = 'SQ:AMOR:pico:AMP',
        readpv = 'SQ:AMOR:pico:AMP_RBV',
        abslimits = (0, 5),
        precision = .1,
        visibility = ('metadata', 'namespace'),
    ),
    spinflipper_freq = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Spin Flipper Frequency',
        writepv = 'SQ:AMOR:pico:FREQ',
        readpv = 'SQ:AMOR:pico:FREQ_RBV',
        abslimits = (0, 300000),
        precision = 1,
        visibility = ('metadata', 'namespace'),
    ),
    spin_selection = device('nicos.devices.generic.switcher.Switcher',
        description = 'Polarisation selector',
        moveable = 'spinflipper_amp',
        mapping = {
            'm': 0.0,
            'p': 1.7,
            'down': 0.0,
            'up': 1.7,
        },
        unit = '',
        precision = .1,
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
)

startupcode = '''
spinflipper_freq.start(140200)
'''
