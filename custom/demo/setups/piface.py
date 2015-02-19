description = 'piface-server'
group = 'optional'

devices = dict()

for i in range(8):
    devices['in_%d' % i] = device('devices.taco.DigitalInput',
                                   description='2nd Input',
                                   tacodevice='//172.25.80.97/test/piface/in_%d' % i,
                                   maxage=5,
                                   pollinterval=2)
    devices['out_%d' % i] = device('devices.taco.DigitalOutput',
                                   description='1st Output',
                                   tacodevice='//172.25.80.97/test/piface/out_%d' % i,
                                   maxage=5,
                                   pollinterval=2)
