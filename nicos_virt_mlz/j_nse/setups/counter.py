description = 'Counter card setup'
group = 'lowlevel'

devices = dict(
    selector = device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description = 'Selector',
        userlimits = (0, 1000),
        abslimits = (0, 1000),
        speed = 100.,
        unit = 'Hz',
        fmtstr = '%.0f',
        pollinterval = 0.5,
    ),
    selector_speed_countercard = device(
        'nicos.devices.generic.DeviceAlias',
        alias = 'selector',
        devclass='nicos.core.device.Readable',
        visibility = ('metadata',),
    ),
    anode_events = device(
        'nicos.devices.generic.VirtualCounter',
        description = 'Anode events',
        type = 'monitor',
        pollinterval = 0.5,
    ),
    monbgr = device(
        'nicos.devices.generic.VirtualCounter',
        description='Background monitor',
        type='monitor',
        pollinterval = 0.5,
    ),
    mon1 = device(
        'nicos.devices.generic.VirtualCounter',
        description = 'Monitor',
        type = 'monitor',
        pollinterval = 0.5,
    ),
    timer = device(
        'nicos.devices.generic.VirtualTimer',
        description = 'Counter card timer channel',
        pollinterval = 0.5,
    ),
)
