description = 'Laser distance measurement device in AMOR'

devices = dict(
    dimetix=device('nicos_sinq.amor.devices.dimetix.EpicsDimetix',
                   description='Laser distance measurement device',
                   readpv='SQ:AMOR:DIMETIX:DIST',
                   epicstimeout=3.0,),

    laser_switch=device('nicos_sinq.amor.devices.sps_switch.SpsSwitch',
        description='Laser light controlled by SPS',
        epicstimeout=3.0,
        readpv='SQ:AMOR:SPS1:DigitalInput',
        commandpv='SQ:AMOR:SPS1:Push',
        commandstr="S0001",
        byte=15,
        bit=7,
        mapping={'OFF': False, 'ON': True},
    ),

    xlz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Counter z position distance laser motor',
               motorpv='SQ:AMOR:mota:xlz',
               errormsgpv='SQ:AMOR:mota:xlz-MsgTxt',
               lowlevel=True
               ),

    laser_positioner=device(
        'nicos.devices.generic.Switcher',
        description='Position laser to read components',
        moveable='xlz',
        mapping={'park': -0.1,
                 'analyzer': -24.0,
                 'detector': 0.0,
                 'polarizer': -88.0,
                 'filter': 1000,
                 'sample': -52.0,
                 'slit1': 1000,
                 'slit2': -73.0,
                 'slit3': -63.0,
                 'slit4': -34.0,
                 'selene': -116.0,
                 },
        fallback='<undefined>',
        precision=0
    )
)
