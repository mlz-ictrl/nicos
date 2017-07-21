# -*- coding: utf-8 -*-

description = 'test setup for S7SPS on PANDA'

includes = ['monoturm']

group = 'lowlevel'

devices = dict(
    s7bus = device('nicos_mlz.panda.devices.panda_s7.S7Bus',
                   tacodevice = '//phys.panda.frm2/panda/dp/5',
                   lowlevel = True,
                  ),
    s7coder = device('nicos_mlz.panda.devices.panda_s7.S7Coder',
                     bus = 's7bus',
                     startbyte = 4,      # 0 is endat-coder, 4 is incremental band
                     unit = 'deg',
                     lowlevel = True,
                    ),
    s7motor = device('nicos_mlz.panda.devices.panda_s7.S7Motor',
                  #~ mtt = device('nicos_mlz.panda.devices.panda_s7.S7Motor',
                     bus = 's7bus',
                     unit = 'deg',
                     abslimits = (-132, -20),
                     lowlevel = True,
                    ),
    #~ mtt = device('nicos.devices.generic.Axis',
    mtt = device('nicos_mlz.panda.devices.panda_s7.Panda_mtt',
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
