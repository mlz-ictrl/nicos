description = 'Be filter control'

group = 'lowlevel'

sw_class = 'devices.generic.ManualSwitch'

devices = dict(
    be_filter_in_io =  device(sw_class,
                              description = 'Be filter in IO',
                              lowlevel = True,
                              states = (0, 1),
                             ),
    be_filter_out_io =  device(sw_class,
                               description = 'Be filter out IO',
                               lowlevel = True,
                               states = (0, 1),
                              ),
    be_filter_in = device('treff.button.Button',
                          description = 'Be filter in button',
                          switch = 'be_filter_in_io',
                          lowlevel = True,
                         ),
    be_filter_out = device('treff.button.Button',
                           description = 'Be filter out button',
                           switch = 'be_filter_out_io',
                           lowlevel = True,
                          ),
    be_filter = device('devices.generic.MultiSwitcher',
                       description = 'Shutter control device',
                       moveables = ('be_filter_out', 'be_filter_in', ),
                       mapping = {'out': (1, 0),
                                  'in': (0, 1),
                                 },
                       fallback = 'unknown',
                       precision = (0, 0),
                      ),
)
