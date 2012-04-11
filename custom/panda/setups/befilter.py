#  -*- coding: utf-8 -*-

description = 'Beryllium filter'

includes = ['system']
 
devices = dict(
   
    #~ TBeFilter = device('nicos.panda.betemp.I7033Temp',
            #~ tacodevice='//pandasrv/panda/i7000/betemp',
            #~ warnlevel=80,
            #~ unit='K',
    #~ ),
    TBeFilter = device('nicos.panda.betemp.KL320xTemp',
            beckhoff = 'anablocks_beckhoff',
            addr = 0,
            warnlevel=80,
            unit='K',
    ),
)
