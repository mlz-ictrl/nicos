description = 'Various devices for logical motors in AMOR'

includes = ['sinq_amor_movable']

devices = dict(
    controller = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotorHandler',
        description = 'Logical Motors Controller',
        lowlevel = True,
        loglevel = 'debug'
    ),
    m2t = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotor',
        description = 'Logical motor monochromator two theta',
        motortype = 'm2t',
        controller = 'controller',
    ),
    s2t = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotor',
        description = 'Logical motor sample two theta',
        motortype = 's2t',
        controller = 'controller',
    ),
    ath = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotor',
        description = 'Logical Motor analyser theta',
        motortype = 'ath',
        controller = 'controller',
        loglevel = 'debug'
    ),
    dimetix=device('nicos_sinq.amor.devices.dimetix.EpicsDimetix',
                   description='Laser distance measurement device',
                   readpv='SQ:AMOR:DIMETIX:DIST',
                   epicstimeout=3.0,),

    laser_switch=device(
        'nicos_sinq.amor.devices.sps_switch.SpsSwitch',
        description='Laser light controlled by SPS',
        epicstimeout=3.0,
        readpv='SQ:AMOR:SPS1:DigitalInput',
        commandpv='SQ:AMOR:SPS1:Push',
        commandstr="S0001",
        bytelist=[(15, 7)],
        mapping={'OFF': 0, 'ON': 1}
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
                 'analyser': -24.0,
                 'detector': 0.0,
                 'polariser': -88.0,
                 'sample': -52.0,
                 'slit2': -73.0,
                 'slit3': -63.0,
                 'slit4': -34.0,
                 'selene': -116.0,
                 },
        fallback='<undefined>',
        precision=0
    ),

    Distances = device(
        'nicos_sinq.amor.devices.component_handler.DistancesHandler',
        description='Device to handle distance calculation in AMOR',
        components={
            'polariser': (-232, 0),
            'slit2': (302, 0),
            'slit3': (-22, 0),
            'slit4': (306, 0),
            'sample': (-310, 0),
            'detector': (326, 0),
            'analyser': (310, 0),
            'filter': (-726, 0),
            'slit1': (0, 0)
        },
        fixedcomponents={
            'chopper': 9906,
        },
        switch='laser_switch',
        positioner='laser_positioner',
        dimetix='dimetix'
    )
)
