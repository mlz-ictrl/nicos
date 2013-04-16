#  -*- coding: utf-8 -*-

description = 'test setup for Monowechsler on PANDA'

includes = ['system']

group = 'optional'

devices = dict(
            
        beckhoffdevice = device('panda.wechsler.Beckhoff',
                host='wechsler.panda.frm2',
                lowlevel=True,
                loglevel='info',
                ),
        
    wechsler = device('panda.wechsler.MonoWechsler',
            beckhoff = 'beckhoffdevice',
            loglevel='info',
            ),
            
)

