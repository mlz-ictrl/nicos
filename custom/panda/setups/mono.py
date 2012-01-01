#  -*- coding: utf-8 -*-

#~ includes = ['system']

devices = dict(
    mtt      = device('nicos.generic.VirtualMotor',
                      abslimits = (-125, -25),
                      unit = 'deg'),

    mth      = device('nicos.generic.VirtualMotor',
                      abslimits = (-20, 120),
                      unit = 'deg'),

    mono     = device('nicos.tas.Monochromator',
                      theta='mth',
                      twotheta='mtt',
                      focush=None,
                      focusv=None,
                      dvalue=3.355,
                      order=1,
                      reltheta=True,
                      sidechange=0,
                      focmode='manual',
                      warninterval=10,
                      unit='A-1',
                      abslimits = (0.5, 20),),

    ki       = device('nicos.tas.Wavevector',
                      unit = 'A-1',
                      base = 'mono',
                      tas = 'panda',
                      scanmode = 'CKI',
                      abslimits = (0.5, 20)),
)
