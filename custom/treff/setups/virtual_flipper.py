description = 'Spin flipper'

group = 'lowlevel'

sw_class = 'devices.generic.ManualSwitch'

devices = dict(
    flipper_sw = device(sw_class,
                        description = 'Spin flipper IO',
                        states = (0, 1),
                        fmtstr = '%d',
                        lowlevel = True,
                       ),
    flipper = device('devices.generic.Switcher',
                     description = 'Spin flipper',
                     moveable = 'flipper_sw',
                     mapping = {'on': 1,
                                'off': 0,
                               },
                     precision = 0,
                    ),
)
