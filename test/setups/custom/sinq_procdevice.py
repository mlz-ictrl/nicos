name = 'SINQ ProcDevice'

description = 'Test Setup for ProcDevice class'

includes = ['stdsystem']

devices = dict(
    sleeper = device('nicos_sinq.devices.procdevice.ProcDevice',
        description = 'A sleeping device...',
        subprocess = 'test/setups/custom/test_sleep.sh',
        args = [
            '2',
        ]
    ),
)
