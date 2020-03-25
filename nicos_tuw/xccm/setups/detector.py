description = 'Detector'

group = 'lowlevel'

devices = dict(
    det = device('nicos.devices.generic.Detector',
        description = 'Detector',
        timers = [
            device('nicos_tuw.xccm.devices.detector.Timer',
                digitalio = device('nicos.devices.generic.ManualSwitch',
                    states = [0, 1],
                    fmtstr = '%d',
                ),
            ),
        ],
    ),
)

startupcode = '''
SetDetectors(det)
'''
