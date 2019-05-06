description = 'Sample devices in the SINQ HRPT.'

pvprefix = 'SQ:HRPT:motc:'

devices = dict(
    som=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample omega motor',
               motorpv=pvprefix + 'SOM',
               errormsgpv=pvprefix + 'SOM-MsgTxt',
               precision=0.01,
                   ),
    chpos=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample Changer Position',
               motorpv=pvprefix + 'CHPOS',
               errormsgpv=pvprefix + 'CHPOS-MsgTxt',
               precision=0.01,
               ),
    stx=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample Table X Translation',
               motorpv=pvprefix + 'STX',
               errormsgpv=pvprefix + 'STX-MsgTxt',
               precision=0.01,
               ),
    sty=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample table y translation',
               motorpv=pvprefix + 'STY',
               errormsgpv=pvprefix + 'STY-MsgTxt',
               precision=0.01,
               )

)
