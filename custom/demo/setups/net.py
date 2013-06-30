description = 'networking transfer device'

group = 'lowlevel'

includes = []

devices = dict(
    net_RX = device('demo.net.Network',
                    description = 'Ingoing network transfer rate',
                    interval = 1,
                    interface = 'lo',
                    direction = 'rx',
                    fmtstr = '%.0f',
                    unit = 'Byte/s',
                   ),
    net_TX = device('demo.net.Network',
                    description = 'Outgoing network transfer rate',
                    interval = 1,
                    interface = 'lo',
                    direction = 'tx',
                    fmtstr = '%.0f',
                    unit = 'Byte/s',
                   ),
)
