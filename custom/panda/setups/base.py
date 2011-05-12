#  -*- coding: utf-8 -*-

includes = ['system']

devices = dict(
    panda    = device('nicos.tas.TAS',
                      instrument = 'PANDA',
                      responsible = 'R. Esponsible <responsible@frm2.tum.de>',
                      cell = 'Sample',
                      phi = 'stt',
                      psi = 'sth',
                      mono = 'mono',
                      ana = 'ana',
                      energytransferunit = 'meV',
                      ),

    stt      = device('nicos.virtual.VirtualMotor',
                      abslimits = (-180, 180), 
                      unit = 'deg'),

    sth      = device('nicos.virtual.VirtualMotor',
                      abslimits = (0, 360),
                      unit = 'deg'),

    mono     = device('nicos.virtual.VirtualMotor',
                      unit = 'A-1',
                      abslimits = (0, 10)),

    ana      = device('nicos.virtual.VirtualMotor',
                      unit = 'A-1',
                      abslimits = (0, 10)),

    ki       = device('nicos.tas.Wavevector',
                      unit = 'A-1',
                      base = 'mono',
                      tas = 'panda',
                      opmode = 'CKI',
                      abslimits = (0, 10)),

    kf       = device('nicos.tas.Wavevector',
                      unit = 'A-1',
                      base = 'ana',
                      tas = 'panda',
                      opmode = 'CKF',
                      abslimits = (0, 10)),
)
