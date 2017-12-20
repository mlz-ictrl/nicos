description = 'networking transfer device'
group = 'optional'

devices = dict(
    net_RX = device('nicos_demo.demo.devices.net.Network',
        description = 'Ingoing network transfer rate',
        interval = 1,
        direction = 'rx',
        fmtstr = '%.0f',
        unit = 'Byte/s',
    ),
    net_TX = device('nicos_demo.demo.devices.net.Network',
        description = 'Outgoing network transfer rate',
        interval = 1,
        direction = 'tx',
        fmtstr = '%.0f',
        unit = 'Byte/s',
    ),
)
