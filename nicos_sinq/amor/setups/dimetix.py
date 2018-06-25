description = 'Laser distance measurement device in AMOR'

devices = dict(
    dimetix=device('nicos_sinq.amor.devices.dimetix.EpicsDimetix',
                   description='Laser distance measurement device',
                   readpv='SQ:AMOR:DIMETIX:DIST',
                   epicstimeout=3.0,
                   switchstates={'on': 1, 'off': 0},
                   switchpvs={'read': 'SQ:AMOR:DIMETIX:LASER',
                              'write': 'SQ:AMOR:DIMETIX:LASER'}, ),
    laser=device(
        'nicos_sinq.amor.devices.programmable_unit.ProgrammableUnit',
        description='Laser light controlled by SPS',
        epicstimeout=3.0,
        readpv='SQ:AMOR:SPS1:DigitalInput',
        commandpv='SQ:AMOR:SPS1:Push',
        commandstr="S0001",
        byte=15,
        bit=7,
        mapping={'OFF': 0, 'ON': 1}
    ),

    xlz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Counter z position distance laser motor',
               motorpv='SQ:AMOR:mota:xlz',
               errormsgpv='SQ:AMOR:mota:xlz-MsgTxt',
               ),
)
