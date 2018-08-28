description = 'Slit 5 devices in the SINQ AMOR.'

group = 'lowlevel'

pvprefix = 'SQ:AMOR:motc:'

devices = dict(
    d5v=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 5 vertical motor',
               motorpv=pvprefix + 'd5v',
               errormsgpv=pvprefix + 'd5v-MsgTxt',
               ),
    d5h=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 5 horizontal motor',
               motorpv=pvprefix + 'd5h',
               errormsgpv=pvprefix + 'd5h-MsgTxt',
               ),
)
