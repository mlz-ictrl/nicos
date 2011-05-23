#  -*- coding: utf-8 -*-

name = 'test setup for 8 axes in 1 Motorrahmen'

includes = ['system']

devices = dict(
    #bus = device('nicos.panda.ne4110a.IPCModBusTCP',
    #             loglevel = 'debug',
    #             host = '172.25.15.51'),
    bus = device('nicos.panda.ne4110a.IPCModBusSerial',
               host = '/dev/ttyS0'),
)

for i in range(1,9):
    devices['s%d' % i] = device('nicos.ipc.Motor', bus='bus', addr=0x50+i, slope=1, unit='steps', abslimits=(0, 999999))
    devices['c%d' % i] = device('nicos.ipc.Coder', bus='bus', addr=0x70+i, slope=2**26/360., unit='steps')
    devices['p%d' % i] = device('nicos.ipc.Coder', bus='bus', addr=0x60+i, slope=1, unit='steps')

#devices['a2'] = device('nicos.axis.Axis', motor='s2', coder='c2', precision=

startupcode=''
