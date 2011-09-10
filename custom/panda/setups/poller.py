#  -*- coding: utf-8 -*-

name = 'setup for the poller'
group = 'special'

includes = ['devices']

devices = dict(
    Poller = device('nicos.poller.Poller',
                    processes={'motors': ['a1'], 'detectors': ['det']}),
)
