description = 'doppler control devices'

group = 'optional'

tango_base = 'tango://phys.spheres.frm2:10000/spheres/'

devices = dict(
    doppler_switch    = device('nicos.devices.tango.NamedDigitalOutput',
                               description = 'switch doppler on and off',
                               tangodevice = tango_base + 'doppler/switch',
                               mapping = {
                                   'on': 1,
                                   'off': 0
                               },
                              ),
    doppler_speed     = device('nicos.devices.tango.AnalogOutput',
                               description = 'Controller for the speed of the '
                                             'doppler',
                               tangodevice = tango_base + 'doppler/speed',
                               unit = 'm/s',
                               lowlevel = True,
                              ),
    doppler_amplitude = device('nicos.devices.tango.AnalogOutput',
                               description = 'Controller for the amplitude of '
                                             'the doppler',
                               tangodevice = tango_base + 'doppler/amplitude',
                               unit = 'mm',
                               lowlevel = True,
                              ),
    doppler           = device('nicos.devices.generic.switcher.MultiSwitcher',
                               description = 'switcher to set speed and '
                                             'amplitude',
                               moveables = [
                                   'doppler_speed',
                                   'doppler_amplitude',
                                   'doppler_switch',
                               ],
                               precision = [0.001, 0.01, None],
                               unit = 'm/s',
                               mapping = {
                                   0.0: (0.3, 25, 'off'),
                                   0.3: (0.3, 25, 'on'),
                                   0.5: (0.5, 30, 'on'),
                                   0.7: (0.7, 35, 'on'),
                                   1.0: (1.0, 40, 'on'),
                                   1.3: (1.3, 45, 'on'),
                                   1.6: (1.6, 50, 'on'),
                                   2.0: (2.0, 60, 'on'),
                                   2.4: (2.4, 60, 'on'),
                                   2.9: (2.9, 75, 'on'),
                                   3.4: (3.4, 75, 'on'),
                                   3.9: (3.9, 75, 'on'),
                                   4.4: (4.4, 75, 'on'),
                                   4.7: (4.7, 75, 'on'),
                               },
                              )
)
