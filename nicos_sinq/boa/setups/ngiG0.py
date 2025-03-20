description = 'Setup for the source grating for fraing interferometry'

pvprefix = 'SQ:BOA:turboPmac3:'

devices = dict(
    ngit = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Grating translation',
        motorpv = pvprefix + 'NGIT',
    ),
    ngir = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Grating rotation',
        motorpv = pvprefix + 'NGIR',
    ),
)
