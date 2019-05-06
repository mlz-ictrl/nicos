description = 'HRPT Bunker primary collimator'

pvprefix = 'SQ:HRPT:motd:'

devices = dict(
    cex1=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Primary Kollimator 1 Motor',
               motorpv=pvprefix + 'CEX1',
               errormsgpv=pvprefix + 'CEX1-MsgTxt',
               precision=0.5,
                   ),
    cex2=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Primary Kollimator 2 Motor',
               motorpv=pvprefix + 'CEX2',
               errormsgpv=pvprefix + 'CEX2-MsgTxt',
               precision=0.5,
               ),
)
