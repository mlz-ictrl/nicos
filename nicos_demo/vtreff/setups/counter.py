# -*- coding: utf-8 -*-

description = 'counter setup'
group = 'lowlevel'

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'ZEA-2 counter card timer channel',
    ),
    mon0 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 0',
        type = 'monitor',
        fmtstr = '%d',
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 1',
        type = 'monitor',
        fmtstr = '%d',
    ),
)
