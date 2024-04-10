description = 'x-ray tube'

group = 'optional'

tango_base = configdata('instrument.values')['tango_base'] + 'box/bruker/'

devices = dict(
    t_shutter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'main shutter for the x-ray source',
        tangodevice = tango_base + 'shutter',
        unit = '',
    ),
    t_shutter_time = device('nicos.devices.entangle.AnalogInput',
        description = 'open time of the shutter',
        tangodevice = tango_base + 'shuttertime',
    ),
    t_anode = device('nicos.devices.generic.ParamDevice',
        description = 'X-ray tube anode material',
        device = 'image',
        parameter = 'anode',
    ),
)
