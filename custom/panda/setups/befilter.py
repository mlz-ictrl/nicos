#  -*- coding: utf-8 -*-

description = 'Beryllium filter'

includes = ['ana'] # should include anablocks

group = 'optional'

devices = dict(
    TBeFilter = device('panda.betemp.KL320xTemp',
                       beckhoff = 'anablocks_beckhoff',
                       addr = 0,
                       warnlimits = (0, 80),
                       unit='K',
                       description = 'Temperature of the Be-Filter or 1513.4K if not used',
                      ),
)
