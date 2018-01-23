description = 'Mini chopper timing driver'

devices = dict(
        chop_ref=
            device('nicos_ess.v20.devices.chopper.EpicsFloatReadable',
                   pollinterval=0.5,
                   description='Ref information of chopper 01',
                   readpv='HZB-V20:Chop-Drv-01:Ref',
                   ),

        chop_tdc=
            device('nicos_ess.v20.devices.chopper.EpicsFloatReadable',
                   pollinterval=0.5,
                   description='TDC information of chopper 01',
                   readpv='HZB-V20:Chop-Drv-01:TDC',
                   ),

        chop_pd=
            device('nicos_ess.v20.devices.chopper.EpicsFloatMoveable',
                   pollinterval=0.5,
                   description='Phase Delay control of chopper 01',
                   readpv='HZB-V20:Chop-Drv-01:PD',
                   writepv='HZB-V20:Chop-Drv-01:PD',
                   ),

        chop_pw=
            device('nicos_ess.v20.devices.chopper.EpicsFloatMoveable',
                   pollinterval=0.5,
                   description='Phase Width control of chopper 01',
                   readpv='HZB-V20:Chop-Drv-01:PW',
                   writepv='HZB-V20:Chop-Drv-01:PW',
                   ),
    )

