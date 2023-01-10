description = '8 channel digital I/O box'

group = 'plugplay'

tango_base = 'tango://flipbox:10000/test/piface/'

excludes = ['pibox01']

devices = {}

for i in range(0, 8):
    devices['in_%i' % i] = device('nicos.devices.entangle.DigitalInput',
        description = 'Input pin %i' % i,
        tangodevice = tango_base + 'in_%i' % i,
        visibility = (),
    )
    devices['out_%i' % i] = device('nicos.devices.entangle.DigitalOutput',
        description = 'Output pin %i' % i,
        tangodevice = tango_base + 'out_%i' % i,
        visibility = (),
    )

devices['out_1'][1]['visibility'] = {'metadata', 'devlist', 'namespace'}
