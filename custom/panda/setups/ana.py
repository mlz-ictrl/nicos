#  -*- coding: utf-8 -*-

#~ includes = ['system']

devices = dict(
    att      = device('nicos.generic.VirtualMotor',
                      abslimits = (-180, 180), 
                      unit = 'deg'),

    ath      = device('nicos.generic.VirtualMotor',
                      abslimits = (-5, 185),
                      unit = 'deg'),

    ana     = device('nicos.tas.Monochromator',
                      theta='ath',
                      twotheta='att',
                      focush=None,
                      focusv=None,
                      dvalue=3.355,
                      order=1,
                      reltheta=False,
                      sidechange=1,
                      focmode='manual',
                      warninterval=10,
                      unit='A-1',
                      abslimits = (0.5, 20)),

    kf       = device('nicos.tas.Wavevector',
                      unit = 'A-1',
                      base = 'ana',
                      tas = 'panda',
                      scanmode = 'CKF',
                      abslimits = (0.5, 20)),
)