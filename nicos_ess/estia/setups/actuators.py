description = 'Prototype actuator motors'

pvprefix = 'PSI-ESTIARND:MC-MCU-01:'

devices = dict(
    am1=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Eksma Actuator',
               motorpv=pvprefix + 'm3',
               errormsgpv=pvprefix + 'm3-MsgTxt',
               ),
    am2=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Phytron Actuator',
               motorpv=pvprefix + 'm5',
               errormsgpv=pvprefix + 'm5-MsgTxt',
               ),
    am3=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Differential Actuator',
               motorpv=pvprefix + 'm4',
               errormsgpv=pvprefix + 'm4-MsgTxt',
               ),
)
