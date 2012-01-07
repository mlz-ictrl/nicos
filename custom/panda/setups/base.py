#  -*- coding: utf-8 -*-

name='base system'

group='internal'

includes = ['mono', 'ana', 'system']

modules=[]


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
                      scatteringsense=(-1,1,-1),
                      ),

    stt      = device('nicos.generic.VirtualMotor',
                      abslimits = (-180, 180),
                      unit = 'deg'),

    sth      = device('nicos.generic.VirtualMotor',
                      abslimits = (0, 360),
                      unit = 'deg'),

    sw       = device('nicos.generic.ManualSwitch',
                      states = ['on','off',2,1],
                      ),

)

startupcode=''
