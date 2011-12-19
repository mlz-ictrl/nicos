#  -*- coding: utf-8 -*-

name = 'test setup for Monowechsler on PANDA'

includes = ['system']

#sysconfig = {'cache': None} # disables Cache completely

devices = dict(
            
        beckhoffdevice = device('nicos.panda.wechsler.Beckhoff',
                host='wechsler.panda.frm2',
                lowlevel=True,
                loglevel='info',
                ),
        
    wechsler = device('nicos.panda.wechsler.MonoWechsler',
            beckhoff = 'beckhoffdevice',
            loglevel='info',
            ),
            
)

