description = 'granite beam movement'

display_order = 80

pvprefix = 'SQ:AMOR:turboPmac3:'

devices = dict(
    granite_beam_shift = device('nicos_sinq.devices.epics.motor.SinqMotor',
                                description = 'Granite beam shift',
                                motorpv = pvprefix + 'beam_shift',
                                visibility = ('metadata', 'namespace'),
                                unit='mm',
                                requires = {'level': 'admin'},
                                ),
    )

