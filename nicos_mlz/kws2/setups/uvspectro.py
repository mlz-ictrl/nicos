# -*- coding: utf-8 -*-

description = 'controlling the UV-vis spectrometer and LEDs'
group = 'optional'

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    OceanView = device('nicos.devices.tango.DigitalOutput',
        description = 'spectrometer trigger interval (0 to switch off)',
        tangodevice = tango_base + 'uvspectro/plc_trigger',
    ),
    LEDdelay = device('nicos.devices.tango.DigitalOutput',
        description = 'delay for LEDs switching on',
        tangodevice = tango_base + 'uvspectro/plc_leddelay',
    ),
    LEDswitch = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'LED switcher',
        tangodevice = tango_base + 'uvspectro/plc_led',
        mapping = {'off': 0, 'uv': 1, 'blue': 2},
    ),
)
