description = 'Prototype actuator motors'

pvprefix = 'PSI-ESTIARND:MC-MCU-01:'

devices = dict(
    am1 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Eksma Actuator',
        motorpv = pvprefix + 'm3',
        errormsgpv = pvprefix + 'm3-MsgTxt',
        errorbitpv = pvprefix + 'm3-Err',
        reseterrorpv = pvprefix + 'm3-ErrRst',
    ),
)
