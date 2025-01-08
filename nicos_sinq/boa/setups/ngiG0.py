description = 'Setup for the source grating for fraing interferometry'

pvprefix = 'SQ:BOA:mcu3:'

devices = dict(
    ngit = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Grating translation',
        motorpv = pvprefix + 'NGIT',
        errormsgpv = pvprefix + 'NGIT-MsgTxt',
        can_disable = True,
    ),
    ngir = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Grating rotation',
        motorpv = pvprefix + 'NGIR',
        errormsgpv = pvprefix + 'NGIR-MsgTxt',
        can_disable = True,
    ),
)
