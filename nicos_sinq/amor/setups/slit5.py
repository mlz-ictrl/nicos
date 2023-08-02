description = 'Slit 5 devices in the SINQ AMOR.'

group = 'lowlevel'

pvprefix = 'SQ:AMOR:motc:'

devices = dict(
    d5v=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Slit 5 vertical motor',
               motorpv=pvprefix + 'd5v',
               errormsgpv=pvprefix + 'd5v-MsgTxt',
               ),
    d5h=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Slit 5 horizontal motor',
               motorpv=pvprefix + 'd5h',
               errormsgpv=pvprefix + 'd5h-MsgTxt',
               ),
)
