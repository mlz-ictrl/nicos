description = 'Shutter control'

group = 'lowlevel'

sw_class = 'devices.generic.ManualSwitch'

devices = dict(
    shutter_open_io =  device(sw_class,
                              description = 'Shutter open IO',
                              lowlevel = True,
                              states = (0, 1),
                             ),
    shutter_close_io =  device(sw_class,
                               description = 'Shutter close IO',
                               lowlevel = True,
                               states = (0, 1),
                              ),
    shutter_open = device('treff.button.Button',
                          description = 'Shutter open button',
                          switch = 'shutter_open_io',
                          lowlevel = True,
                         ),
    shutter_close = device('treff.button.Button',
                          description = 'Shutter close button',
                          switch = 'shutter_close_io',
                          lowlevel = True,
                         ),
    shutter = device('devices.generic.MultiSwitcher',
                     description = 'Shutter control device',
                     moveables = ('shutter_close', 'shutter_open', ),
                     mapping = {'closed': (1, 0),
                                'open': (0, 1),
                               },
                     fallback = 'unknown',
                     precision = (0, 0),
                    ),
)
