# -*- coding: utf-8 -*-

description = 'test setup for S7SPS on PANDA'

includes = ['monoturm']

group = 'lowlevel'

devices = dict(
    s7bus = device('panda.panda_s7.S7Bus',
                   tacodevice = 'panda/dp/5',
                   lowlevel = True,
                  ),
    s7coder = device('panda.panda_s7.S7Coder',
                     bus = 's7bus',
                     startbyte = 4,      # 0 is endat-coder, 4 is incremental band
                     unit = 'deg',
                     lowlevel = True,
                    ),
    s7motor = device('panda.panda_s7.S7Motor',
                  #~ mtt = device('panda.panda_s7.S7Motor',
                     bus = 's7bus',
                     unit = 'deg',
                     abslimits = (-132, -20),
                     lowlevel = True,
                    ),
    #~ mtt = device('devices.generic.Axis',
    mtt = device('panda.panda_s7.Panda_mtt',
                 description = "PANDA's main Axis, TwoTheta of Monochromator",
                 unit = 'deg',
                 abslimits = (-132, -20),
                 coder = 's7coder',
                 motor = 's7motor',
                 obs = ['mtt_enc'],
                 precision = 0.01,
                 offset = 0.6,
                 dragerror = -1.,    # do not check drag errors as this is done in SPS
                 jitter = 0.5,       # work around a bug in S7
                ),
)



#startupcode = '''
#SetMode('maintenance') # automagically switch to maintenance (master) modus
#print 'ignore next two lines.....'
#'''
