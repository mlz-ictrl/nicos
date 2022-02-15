description = 'Selene support devices in AMOR'

pvprefix = 'SQ:AMOR:mota:'

devices = dict(
    eoz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               description='Counter z lift Selene support motor',
               motorpv=pvprefix + 'eoz',
               errormsgpv=pvprefix + 'eoz-MsgTxt',
               ),
    eom=device('nicos_ess.devices.epics.motor.EpicsMotor',
               description='Counter omega Selene support motor',
               motorpv=pvprefix + 'eom',
               errormsgpv=pvprefix + 'eom-MsgTxt',
               ),
)
