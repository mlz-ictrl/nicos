#  -*- coding: utf-8 -*-

name = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    alwayspoll = [],
                    blacklist = ['tas']),
)
