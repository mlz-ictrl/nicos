# -*- coding: utf-8 -*-

description = 'JCNS motor control'

group = 'optional'

includes = []

tango_base = 'tango://slow.antares.frm2:10000/antares/'

devices = dict(
    # MonoSwitch
    monoswitch_io = device('devices.tango.DigitalOutput',
                           description = 'Tango device for Monoswitch in/out',
                           tangodevice = tango_base + 'fzjdp_digital/Monochromator',
                           lowlevel = True,
                          ),
    monoswitch = device('devices.generic.Switcher',
                        description = 'Monochromator switch in/out',
                        moveable = 'monoswitch_io',
                        mapping = {'in': 1, 'out': 2},
                        fallback = '<undefined>',
                        precision = 0,
                       ),
)


startupcode = '''
'''
