description = 'Autokollimator von Trioptic'

# not included by others
group = 'optional'

uribase = 'tango://refsans10.refsans.frm2:10000/refsans/flipper/'

devices = dict(
    _guide = device('devices.tango.AnalogInput',
                   description = 'Temperature of Flipping Guide',
                   tangodevice = uribase + 'guide_temp',
                  ),
    _coil = device('devices.tango.AnalogInput',
                  description = 'Temperature of Flipping Coil',
                  tangodevice = uribase + 'coil_temp',
                 ),
    _current = device('devices.tango.WindowTimeoutAO',
                     description = 'Current of Flipping Coil',
                     tangodevice = uribase + 'current',
                     precision = 0.1,
                    ),
    _frequency = device('devices.tango.AnalogInput',
                       description = 'Frequency of Flipping Field',
                       tangodevice = uribase + 'frequency',
                      ),
    _flipper = device('devices.tango.NamedDigitalOutput',
                     description = 'Flipper',
                     tangodevice = uribase + 'flipper',
                     mapping = dict(ON=1, OFF=0),
                    ),
)

startupcode = """
"""

