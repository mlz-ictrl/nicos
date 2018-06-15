description = 'doppler control devices'

group = 'optional'

nethost = 'phys.spheres.frm2'
doppler = 'tango://%s:10000/spheres/doppler/' % nethost

devices = dict(
    doppler_switch = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Switch doppler on and off',
        tangodevice = doppler + 'switch',
        mapping = {'on': 1,
                   'off': 0},
        lowlevel = True,
    ),
    doppler_speed = device('nicos.devices.tango.AnalogOutput',
        description = 'Controller for the speed of the doppler',
        tangodevice = doppler + 'speed',
        unit = 'm/s',
        lowlevel = True,
    ),
    doppler_amplitude = device('nicos.devices.tango.AnalogOutput',
        description = 'Controller for the amplitude of the doppler',
        tangodevice = doppler + 'amplitude',
        unit = 'mm',
        lowlevel = True,
    ),
    doppler = device('nicos_mlz.spheres.devices.doppler.Doppler',
        description = 'Switcher to control the doppler',
        moveables = ['doppler_speed', 'doppler_amplitude', 'doppler_switch'],
        precision = [0.0001, 0, None],
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
        fallback = 'undefinded',
        pollinterval = 5
    )
)
