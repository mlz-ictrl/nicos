description = 'Reading Keithley multimeter as a counter'

group = 'optional'

includes = ['busk6221 ']

excludes = ['delta']

devices = dict(
    Delta = device('nicos_mgml.devices.keithley.Deltameter',
        description = 'Deltameter',
        fmtstr = '%.8f',
        k6221 = 'busk6221',
        k7001 = None,
    ),
)
