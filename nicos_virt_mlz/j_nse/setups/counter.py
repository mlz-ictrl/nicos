description = 'Counter card setup'
group = 'lowlevel'

includes = [
    'selector',
]

devices = dict(
    selector_cts = device(
        'nicos_virt_mlz.j_nse.devices.Integrator',
        description = 'Selector counter',
        unit = 'cts',
        informula = 'x',
        dev = 'selector_freq',
        fmtstr = '%.0f',
    ),
    selector_freq = device(
        'nicos_mlz.refsans.devices.converters.LinearKorr',
        description = 'Selector frequency',
        unit = 'Hz',
        informula = 'x / 60',
        dev = 'selector_speed',
        fmtstr = '%.0f',
    ),
    anode_events = device(
        'nicos.devices.generic.VirtualCounter',
        description = 'Anode events',
        type = 'monitor',
    ),
    monbgr = device(
        'nicos.devices.generic.VirtualCounter',
        description='Background monitor',
        type='monitor',
    ),
    mon1 = device(
        'nicos.devices.generic.VirtualCounter',
        description = 'Monitor',
        type = 'monitor',
    ),
    timer = device(
        'nicos.devices.generic.VirtualTimer',
        description = 'Counter card timer channel',
    ),
)
