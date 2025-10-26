description = 'ZEA-2 counter card setup'
group = 'lowlevel'

devices = dict(
    mon1 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 1',
        type = 'monitor',
        fmtstr = '%d',
    ),
)
