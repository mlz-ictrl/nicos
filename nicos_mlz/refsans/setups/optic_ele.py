description = 'NOK Devices for REFSANS, main file including all'

group = 'lowlevel'

excludes = ['optic_elements']

includes = [# 'nok2',
            # 'nok3',
            # 'nok4',
            # 'b1',
            # 'disc3',
            # 'disc4',
            # 'nok5a',
            # 'zb0',
            'nok5b',
            # 'zb1',
            # 'nok6',
            # 'zb2',
            # 'nok7',
            # 'zb3',
            # 'nok8',
            # 'bs1',
            # 'nok9',
            # 'sc2',
            # 'b2',
            # 'b3',
            # 'h2',
            ]

devices = dict(
    optic = device('nicos_mlz.refsans.devices.optic.Optic',
        description = 'Beam optic',
        # nok2 = 'nok2',
    ),
)
