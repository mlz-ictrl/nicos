description = 'BOA Translations stages'

pvprefix = 'SQ:BOA:turboPmac2:'

devices = dict(
    translation_300mm_a = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Translation 1',
        motorpv = pvprefix + 'TVA',
    ),
    translation_300mm_b = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Translation 2',
        motorpv = pvprefix + 'TVB',
    ),
)
