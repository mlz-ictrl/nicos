description = 'Refsans_flipper special HW'

# not included by others
group = 'optional'

uribase = 'tango://refsansctrl01.refsans.frm2:10000/refsans/flipper/'

devices = dict(
    guide = device('devices.tango.AnalogInput',
                   description = 'Temperature of Flipping Guide',
                   tangodevice = uribase + 'guide_temp',
                  ),
    coil = device('devices.tango.AnalogInput',
                  description = 'Temperature of Flipping Coil',
                  tangodevice = uribase + 'coil_temp',
                 ),
    current = device('devices.tango.WindowTimeoutAO',
                     description = 'Current of Flipping Coil',
                     tangodevice = uribase + 'current',
                     precision = 0.1,
                    ),
    frequency = device('devices.tango.AnalogInput',
                       description = 'Frequency of Flipping Field',
                       tangodevice = uribase + 'frequency',
                      ),
    flipper = device('devices.tango.NamedDigitalOutput',
                     description = 'Flipper',
                     tangodevice = uribase + 'flipper',
                     mapping = dict(ON=1, OFF=0),
                    ),
)
