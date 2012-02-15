#  -*- coding: utf-8 -*-

description = 'Beryllium filter'

includes = ['system']
 
devices = dict(
   
    TBeFilter = device('nicos.panda.betemp.I7033Temp',
            tacodevice='//pandasrv/panda/i7000/betemp',
            warnlevel=80,
            unit='K',
    ),
)
