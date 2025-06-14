description = 'SANS shutter via SPS-5'

group = 'lowlevel'

devices = dict(
    shutter = device('nicos_sinq.amor.devices.sps_switch.SpsSwitch',
        description = 'Shutter SPS',
        readpv = 'SQ:SANS:SPS1:DigitalInput',
        commandpv = 'SQ:SANS:SPS1:Push',
        commandstr = "S0000",
        byte = 5,
        bit = 1,
        mapping = {
            'open': False,
            'closed': True
        },
    ),
    sps1 = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Controller of the SPS-S5',
        commandpv = 'SQ:SANS:spsdirect.AOUT',
        replypv = 'SQ:SANS:spsdirect.AINP',
    ),
)
