description = 'D1 Slit at HRPT'

pvprefix  = 'SQ:HRPT:motb:'

devices = dict(
    d1r=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='D1 Slit Right Blade',
               motorpv=pvprefix + 'D1R',
               errormsgpv=pvprefix + 'D1R-MsgTxt',
               precision=0.01,
               ),

    d1l=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='D1 Slit Left Blade',
               motorpv=pvprefix + 'D1L',
               errormsgpv=pvprefix + 'D1L-MsgTxt',
               precision=0.01,
               ),

    )
