description = 'piface box'
group = 'plugplay'

nethost = setupname

devices = dict(
    in_all = device('devices.taco.DigitalInput',
                    description = 'All inputs in one device',
                    tacodevice = '//%s/box/piface/in_all' % nethost,
                    maxage = 5,
                    fmtstr = '0x%02x',
                    pollinterval = 2),
    out_all = device('devices.taco.DigitalOutput',
                     description = 'All outputs in one device',
                     tacodevice = '//%s/box/piface/out_all' % nethost,
                     maxage = 5,
                     fmtstr = '0x%02x',
                     pollinterval = 2),
)

for i in range(8):
    devices['in_%d' % i] = device('devices.taco.DigitalInput',
                                  description = '%d. Input' % i,
                                  tacodevice = '//%s/box/piface/in_%d' % (nethost, i,),
                                  maxage = 5,
                                  pollinterval = 2)
    devices['out_%d' % i] = device('devices.taco.DigitalOutput',
                                   description = '%d. Output' % i,
                                   tacodevice = '//%s/box/piface/out_%d' % (nethost, i,),
                                   maxage =5,
                                   pollinterval = 2)
