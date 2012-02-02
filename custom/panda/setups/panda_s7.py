#  -*- coding: utf-8 -*-

description = 'test setup for S7SPS on PANDA'

includes = ['monoturm']


devices = dict(
	s7bus=device('nicos.panda.panda_s7.S7Bus',
		tacodevice='panda/dp/5',
		lowlevel=True,
		),
	s7coder=device('nicos.panda.panda_s7.S7Coder',
		bus='s7bus',
		startbyte=4,	# 0 is endat-coder, 4 is incremental band
		unit='deg',
		abslimits=(-132, -20),
		),
	s7motor=device('nicos.panda.panda_s7.S7Motor',
		bus='s7bus',
		unit='deg',
		abslimits=(-132, -20),
		),
	mtt=device('nicos.generic.Axis',
		unit='deg',
		abslimits=(-132, -20),
		coder='mtt_enc',
		motor='s7motor',
		obs=['s7coder'],
		precision=0.01,
		),
)


#devices['a2'] = device('nicos.axis.Axis', motor='s2', coder='c2', precision=

#startupcode='''
#SetMode('maintenance')  # automagically switch to maintenance (master) modus
#print 'ignore next two lines.....'
#'''
