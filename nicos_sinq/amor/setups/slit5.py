description = 'Slit 5 devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motc:'

devices = dict(
    d5v=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 5 vertical motor',
               motorpv=pvprefix + 'd5v',
               errormsgpv=pvprefix + 'd5v-MsgTxt',
               lowlevel=True
               ),
    d5h=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 5 horizontal motor',
               motorpv=pvprefix + 'd5h',
               errormsgpv=pvprefix + 'd5h-MsgTxt',
               lowlevel=True
               ),
    slit5=device('nicos.devices.generic.slit.TwoAxisSlit',
                 description='Slit 5 controller',
                 horizontal='d5h',
                 vertical='d5v'
                 ),
)
