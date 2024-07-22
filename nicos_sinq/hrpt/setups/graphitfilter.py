description = 'HRPT Graphit Filter via SPS-S5'

devices = dict(
    graphit = device('nicos_sinq.devices.s5_switch.S5Switch',
        description = 'Graphit filter controlled by SPS',
        readpv = 'SQ:HRPT:SPS1:DigitalInput',
        commandpv = 'SQ:HRPT:SPS1:Push',
        commandstr = "S0001",
        byte = 4,
        bit = 4,
        sps_timeout = 90,
        mapping = {
            'OFF': False,
            'ON': True
        },
        visibility = ('metadata', 'namespace', 'devlist'),
    ),
)
