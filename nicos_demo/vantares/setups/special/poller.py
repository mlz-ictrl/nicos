#  -*- coding: utf-8 -*-

description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        description = 'Device polling service',
        alwayspoll = [],
        neverpoll = [],
        blacklist = [],  # ['tas'],
    ),
)
