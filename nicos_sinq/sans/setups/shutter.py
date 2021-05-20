description = 'SANS shutter via SPS-5'

devices = dict(
    shutter = device('nicos_sinq.amor.devices.sps_switch.SpsSwitch',
        description = 'Shutter SPS',
        epicstimeout = 3.0,
        readpv = 'SQ:SANS:SPS1:DigitalInput',
        commandpv = 'SQ:SANS:SPS1:Push',
        commandstr = "S0000",
        byte = 5,
        bit = 1,
        mapping = {
            'open': False,
            'closed': True
        },
        lowlevel = False
    ),
    sps1 = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout = 3.0,
        description = 'Controller of the SPS-S5',
        commandpv = 'SQ:SANS:spsdirect.AOUT',
        replypv = 'SQ:SANS:spsdirect.AINP',
    ),
)
