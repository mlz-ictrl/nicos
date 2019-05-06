description='HRPT Graphit Filter via SPS-S5'

devices = dict(
    graphit=device('nicos_sinq.amor.devices.sps_switch.SpsSwitch',
                        description='Graphit filter controlled by SPS',
                        epicstimeout=3.0,
                        readpv='SQ:HRPT:SPS1:DigitalInput',
                        commandpv='SQ:HRPT:SPS1:Push',
                        commandstr="S0001",
                        byte=4,
                        bit=4,
                        mapping={'OFF': False, 'ON': True},
                        lowlevel=True
                        ),
    sps1=device(
        'nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout=3.0,
        description='Controller of the counter box',
        commandpv='SQ:HRPT:spsdirect.AOUT',
        replypv='SQ:HRPT:spsdirect.AINP',
    ),
)
