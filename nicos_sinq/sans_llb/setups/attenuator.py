description = 'Attenuator Devices'

pvprefix = 'SQ:SANS-LLB:turboPmac2:'

group = 'lowlevel'

devices = dict(
    attpos = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Mask/Attenuator stage rotation',
        motorpv = pvprefix + 'attpos',
        visibility = {'metadata', 'namespace'},
    ),
    att = device('nicos.devices.generic.switcher.Switcher',
        description = 'Mask/Attenuator switcher',
        moveable = 'attpos',
        mapping = {
            '0': 0,
            '1': -45,
            '2': -90,
            '3': -135,
            '4': -180,
            '5': -225,
            '6': -270,
            '7': -315
        },
        precision = .1,
        blockingmove = False,
    )
)
