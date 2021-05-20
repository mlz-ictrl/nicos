description = 'Setup for the source grating for fraing interferometry'

pvprefix = 'SQ:BOA:mcu3:'

devices = dict(
    ngit = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Grating translation',
        motorpv = pvprefix + 'NGIT',
        errormsgpv = pvprefix + 'NGIT-MsgTxt',
    ),
    ngir = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Grating rotation',
        motorpv = pvprefix + 'NGIR',
        errormsgpv = pvprefix + 'NGIR-MsgTxt',
    ),
)
