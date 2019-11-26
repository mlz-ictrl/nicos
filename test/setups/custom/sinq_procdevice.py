name = 'SINQ ProcDevice'

description = 'Test Setup for ProcDevice class'

includes = ['stdsystem']

devices = dict(
    sleeper = device('nicos_sinq.devices.procdevice.ProcDevice',
        description = 'A sleeping device...',
        subprocess = 'sleep',
        args = [
            '2',
        ]
    ),
)
