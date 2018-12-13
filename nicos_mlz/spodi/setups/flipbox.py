description = 'flipbox'

group = 'optional'

nethost = 'flipbox.spodi.frm2'

devices = {}

for i in range(0, 8):
    devices['in_%i' % i] = device('nicos.devices.taco.DigitalInput',
        description = 'Input pin %i' % i,
        tacodevice = '//%s/test/piface/in_%i' % (nethost, i),
        lowlevel = True,
    )
    devices['out_%i' % i] = device('nicos.devices.taco.DigitalOutput',
        description = 'Output pin %i' % i,
        tacodevice = '//%s/test/piface/out_%i' % (nethost, i),
        lowlevel = True,
    )

devices['out_1'][1]['lowlevel'] = False
