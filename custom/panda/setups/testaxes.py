#  -*- coding: utf-8 -*-

description = 'test setup for 8 axes in 1 Motorrahmen'

includes = ['system']

#sysconfig = {'cache': None} # disables Cache completely

devices = dict(
        # using Moxa NE4110A Ethernet-2-Serial converter Box
    #~ #bus = device('nicos.panda.ne4110a.IPCModBusTCP',
    #~ bus = device('nicos.ipc.IPCModBusTCP',
                 #~ #loglevel = 'debug',
                 #~ loglevel = 'info',
		 #~ roundtime = 0.05,
                 #~ host = '172.25.15.51'),
        # using serial cable
    #bus = device('nicos.ipc.IPCModBusSerial',
    #~ #           loglevel = 'debug',
    #~ #           host = '/dev/ttyS0'),
    # 1st Try with TACO RS485 on New Moxa
    bus1 = device('nicos.ipc.IPCModBusTaco',
            tacodevice='//pandasrv/panda/moxa/port1',
            loglevel='info',
            timeout=0.5, ),
            
    bus2 = device('nicos.ipc.IPCModBusTaco',
            tacodevice='//pandasrv/panda/moxa/port2',
            loglevel='info',
            timeout=0.5, ),
            
    bus3 = device('nicos.ipc.IPCModBusTaco',
            tacodevice='//pandasrv/panda/moxa/port3',
            loglevel='info',
            timeout=0.5, ),
            
    bus4 = device('nicos.ipc.IPCModBusTaco',
            tacodevice='//pandasrv/panda/moxa/port4',
            loglevel='info',
            timeout=0.5, ),
            
    bus5 = device('nicos.ipc.IPCModBusTaco',
            tacodevice='//pandasrv/panda/moxa/port5',
            loglevel='info',
            timeout=0.5, ),
            
)

for i in range(1,9):
    devices['s%d' % i] = device('nicos.ipc.Motor', bus='bus2', addr=0x50+i, slope=1., unit='steps', abslimits=(0, 999999),fmtstr='%d')
    devices['p%d' % i] = device('nicos.ipc.Coder', bus='bus2', addr=0x60+i, slope=1., unit='steps')
    devices['c%d' % i] = device('nicos.ipc.Coder', bus='bus2', addr=0x70+i, slope=1., unit='steps')

#devices['a2'] = device('nicos.axis.Axis', motor='s2', coder='c2', precision=

#startupcode='''
#SetMode('maintenance')  # automagically switch to maintenance (master) modus
#print 'ignore next two lines.....'
#'''
