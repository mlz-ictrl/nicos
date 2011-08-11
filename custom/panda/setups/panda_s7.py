#  -*- coding: utf-8 -*-

name = 'test setup for 8 axes in 1 Motorrahmen'

includes = ['system']

#sysconfig = {'cache': None} # disables Cache completely

devices = dict(
    #bus = device('nicos.panda.ne4110a.IPCModBusTCP',
    bus = device('nicos.ipc.IPCModBusTCP',
                 #loglevel = 'debug',
                 loglevel = 'info',
		 roundtime = 0.05,
                 host = '172.25.15.51'),
    #bus = device('nicos.ipc.IPCModBusSerial',
    #           loglevel = 'debug',
    #           host = '/dev/ttyS0'),
	st_mtt=device('nicos.ipc.Motor',
		bus = 'bus',
		addr = 0x51,
		slope = 1,
		unit = 'steps',
		abslimits=(0,999999),
		fmtstr='%d',
		lowlevel=True,
		),
	st_mtt_relays=device('nicos.ipc.MotorRelays',
		stepper = 'st_mtt',
		lowlevel=True,
		),
	st_mtt_inhibit=device('nicos.ipc.MotorInhibit',
		stepper = 'st_mtt',
		lowlevel=True,
		),
	s7bus=device('nicos.panda.panda_s7.S7Bus',
		tacodevice='panda/dp/5',
		lowlevel=True,
		),
	s7coder=device('nicos.panda.panda_s7.S7Coder',
		bus='s7bus',
		startbyte=4,
		unit='deg',
		abslimits=(-140, -20),
		),
	s7motor=device('nicos.panda.panda_s7.S7Motor',
		bus='s7bus',
		unit='deg',
		abslimits=(-140, -20),
		),
	mtt=device('nicos.panda.panda_s7.Panda_mtt',
		unit='deg',
		coder='s7coder',
		motor='s7motor',
		obs=None,
		air_enable='st_mtt_relays',
		air_on='on',
		air_off='off',
		air_sensor='st_mtt_inhibit',
		air_is_on='on',
		startdelay=0,
		stopdelay=2,
		air_timeout=5,
		roundtime=0.2,
		),
)


#devices['a2'] = device('nicos.axis.Axis', motor='s2', coder='c2', precision=

#startupcode='''
#SetMode('maintenance')  # automagically switch to maintenance (master) modus
#print 'ignore next two lines.....'
#'''
