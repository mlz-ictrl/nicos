description = 'All motion stages in the ESSIIP-lab.'

devices = dict(
    m1=device('essiip.epics_motor.EpicsMotor',
              epicstimeout=3.0,
              description='Single axis positioner',
              motorpv='LabS-ESSIIP:MC-MCU-01:m1',
             ),
)
