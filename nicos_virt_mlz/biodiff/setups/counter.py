# -*- coding: utf-8 -*-

description = 'ZEA-2 counter card setup'
group = 'lowlevel'

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'ZEA-2 counter card timer channel',
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 1',
        type = 'monitor',
        fmtstr = '%d',
    ),
)
