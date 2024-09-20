description = 'x-ray tube'

group = 'lowlevel'

tango_base = configdata('instrument.values')['tango_base'] + 'box/bruker/'

includes = ['d8']

devices = dict(
    t_shutter = device('nicos_mlz.labs.physlab.devices.shutter.Shutter',
        description = 'main shutter for the x-ray source',
        tangodevice = tango_base + 'shutter',
        d8 = 'd8',
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
