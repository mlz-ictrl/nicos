description = 'Mini chopper in the ESSIIP lab.'

chopper_number = 1

devices = dict(
        chop_speed=
            device('nicos_ess.v20.devices.chopper.EpicsFloatMoveable',
                   pollinterval=0.5,
                   #abslimits=(0, 14),
                   description='Speed control of chopper {}'.format(chopper_number),
                   readpv='HZB-V20:Chop-CHIC-01:ActSpd',
                   writepv='HZB-V20:Chop-CHIC-01:Spd',
                   lowlevel=True),

        chop_phase=
            device('nicos_ess.v20.devices.chopper.EpicsFloatMoveable',
                   pollinterval=0.5,
                   #abslimits=(0, 360),
                   description='Phase control of chopper {}'.format(chopper_number),
                   readpv='HZB-V20:Chop-CHIC-01:Phs-RB',
                   writepv='HZB-V20:Chop-CHIC-01:Phs',
                   lowlevel=True
                   ),

        chop_park=
            device('nicos_ess.v20.devices.chopper.EpicsFloatMoveable',
                   pollinterval=0.5,
                   #abslimits=(0, 360),
                   description='Park control of chopper {}'.format(chopper_number),
                   readpv='HZB-V20:Chop-CHIC-01:ParkAng-RB',
                   writepv='HZB-V20:Chop-CHIC-01:ParkAng',
                   lowlevel=True
                   ),

        chop_state=
            device('nicos.devices.epics.EpicsReadable',
                   pollinterval=0.5,
                   description='State information of chopper {}'.format(chopper_number),
                   readpv='HZB-V20:Chop-CHIC-01:State',
                   lowlevel=True
                   ),

        chop_command=
            device('nicos_ess.v20.devices.chopper.EpicsEnumMoveable',
                   description='Command interface of chopper {}'.format(
                       chopper_number),
                   readpv='HZB-V20:Chop-CHIC-01:CmdS',
                   writepv='HZB-V20:Chop-CHIC-01:CmdS',
                   lowlevel=True
                   ),

        chopper_1=
            device('nicos_ess.v20.devices.chopper.EssChopper',
                   description='Chopper {}'.format(chopper_number),
                   speed=['chop_speed'],
                   phase=['chop_phase'],
                   parkposition=['chop_park'],
                   state=['chop_state'],
                   command=['chop_command']
                   )
    )
