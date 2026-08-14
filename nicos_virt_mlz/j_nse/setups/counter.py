description = 'Counter card setup'
group = 'lowlevel'

includes = [
    'selector',
]

devices = dict(
    selector_cts = device(
        'nicos_virt_mlz.j_nse.devices.jnse.Integrator',
        description = 'Selector counter',
        unit = 'cts',
        informula = 'x',
        dev = 'selector_freq',
        fmtstr = '%.0f',
        pollinterval = 0.5,
    ),
    selector_freq = device(
        'nicos_mlz.refsans.devices.converters.LinearKorr',
        description = 'Selector frequency',
        unit = 'Hz',
        informula = 'x / 60',
        dev = 'selector_speed',
        fmtstr = '%.0f',
        pollinterval = 0.5,
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
