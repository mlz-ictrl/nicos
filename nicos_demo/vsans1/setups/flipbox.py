description = 'SANS-1 magic box'

group = 'optional'

devices = {}

for i in range(0, 8):
    devices['in_%i' % i] = device('nicos.devices.generic.ManualSwitch',
        description = 'Input pin %i' % i,
        lowlevel = True,
        states = (0, 1),
    )
    devices['out_%i' % i] = device('nicos.devices.generic.ManualSwitch',
        description = 'Output pin %i' % i,
        lowlevel = True,
        states = (0, 1),
    )

devices['out_1'][1]['lowlevel'] = False
