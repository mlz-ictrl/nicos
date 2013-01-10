#  -*- coding: utf-8 -*-

description = 'Beryllium filter'

includes = ['ana'] # should include anablocks
 
devices = dict(
   
    #~ TBeFilter = device('panda.betemp.I7033Temp',
            #~ tacodevice='//pandasrv/panda/i7000/betemp',
            #~ warnlevel=80,
            #~ unit='K',
    #~ ),
    TBeFilter = device('panda.betemp.KL320xTemp',
            beckhoff = 'anablocks_beckhoff',
            addr = 0,
            warnlevel=80,
            unit='K',
            description = 'Temperature of the Be-Filter or 1513.4K if not used',
    ),
)
