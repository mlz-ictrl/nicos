# -*- coding: utf-8 -*-

description = 'test setup for S7SPS on PANDA'

includes = ['monoturm']


devices = dict(
    s7bus = device('panda.panda_s7.S7Bus',
                                    tacodevice = 'panda/dp/5',
                                    lowlevel = True,
                                    ),
    s7coder = device('panda.panda_s7.S7Coder',
                                    bus = 's7bus',
                                    startbyte = 4,	# 0 is endat-coder, 4 is incremental band
                                    unit = 'deg',
                                    abslimits = (-132, -20),
                                    lowlevel = True,
                                    ),
    s7motor = device('panda.panda_s7.S7Motor',
                                    #~ mtt = device('panda.panda_s7.S7Motor',
                                    bus = 's7bus',
                                    unit = 'deg',
                                    abslimits = (-132, -20),
                                    lowlevel = True,
                                    ),
    mtt = device('devices.generic.Axis',
                                    unit = 'deg',
                                    abslimits = (-132, -20),
                                    coder = 's7coder',
                                    motor = 's7motor',
                                    obs = ['mtt_enc'],
                                    precision = 0.01,
                                    #offset = 0.06,
                                    offset = 0.1,
                                    ),
)



#startupcode = '''
#SetMode('maintenance') # automagically switch to maintenance (master) modus
#print 'ignore next two lines.....'
#'''
