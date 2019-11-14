# -*- coding: utf-8 -*-

description = 'doppler control devices'

group = 'lowlevel'

tangohost = 'phys.spheres.frm2'
doppler = 'tango://%s:10000/spheres/doppler/' % tangohost

acqhost = 'phys.spheres.frm2'
acq = 'tango://%s:10000/spheres/sis/' % acqhost

devices = dict(
    doppler_switch = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Switch doppler on and off',
        tangodevice = doppler + 'switch',
        mapping = dict(on=1,
                       off=0),
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
        description = 'Switcher to control the doppler.\n'
                      '"Stop" does not stop doppler movement.\n'
                      'To Stop doppler movement select "Standby" or "0.0"\n'
                      'from the dropdown and click move.\n'
                      'Only set custom values if you know what you are doing!',
        moveables = ['doppler_speed', 'doppler_amplitude'],
        switch = 'doppler_switch',
        acq = 'acqdoppler',
        precision = [0.0001, 0],
        unit = 'm/s',
        customrange = (0.1, 4.7),
        mapping = {
            'Standby': (0,    0),  # values for this are arbitrary
            0.0:       (0,    0),
            0.3:       (0.3, 25),
            0.5:       (0.5, 30),
            0.7:       (0.7, 35),
            1.0:       (1.0, 40),
            1.3:       (1.3, 45),
            1.6:       (1.6, 50),
            2.0:       (2.0, 60),
            2.4:       (2.4, 60),
            2.9:       (2.9, 75),
            3.4:       (3.4, 75),
            3.9:       (3.9, 75),
            4.4:       (4.4, 75),
            4.7:       (4.7, 75),
        },
        fallback = 'undefinded',
        pollinterval = 5,
        margins = dict(speed=0.01,
                       amplitude=0.1)
    ),
    acqdoppler = device('nicos_mlz.spheres.devices.doppler.AcqDoppler',
        description = 'Doppler values as seen by the SIS detector',
        tangodevice = acq + 'counter',
        unit = '',
        fmtstr = '%.3f m/s, %.3f m',
        lowlevel = True,
    ),
)
