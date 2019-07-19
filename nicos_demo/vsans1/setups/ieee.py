description = 'setup for special IEEE devices'

group = 'optional'

devices = dict()

for i in range(1, 11):
    devices['ieee_%d' % i] = device('nicos_mlz.sans1.devices.bersans.IEEEDevice',
        description = 'IEEE device No. %d' % i
    )
