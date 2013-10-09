#  -*- coding: utf-8 -*-

description = 'test setup for Monowechsler on PANDA'

includes = ['system']

group = 'optional'

devices = dict(
    beckhoffdevice = device('panda.wechsler.Beckhoff',
                             description = 'lowlevel device used to communicate with panda\'s monochanger',
                             host='wechsler.panda.frm2',
                             lowlevel=True,
                             loglevel='info',
                            ),
    wechsler = device('panda.wechsler.MonoWechsler',
                       description = 'Monochanger for panda, \\alpha Version!',
                       beckhoff = 'beckhoffdevice',
                       loglevel='info',
                      ),
)
