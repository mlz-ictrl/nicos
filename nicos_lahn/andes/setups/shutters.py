description = 'shutters setup'

group = 'lowlevel'

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    shutter_1=device('nicos.devices.entangle.NamedDigitalInput',
                     description='shutter 1',
                     tangodevice=tango_base + 'shutters/1st',
                     ),
    shutter_2=device('nicos.devices.entangle.NamedDigitalOutput',
                     description='shutter 2',
                     tangodevice=tango_base + 'shutters/2nd',
                     requires={'level': 'admin'},
                     ),
    shutter_3=device('nicos.devices.entangle.NamedDigitalOutput',
                     description='shutter 3',
                     tangodevice=tango_base + 'shutters/3rd',
                     requires={'level': 'admin'},
                     ),
)
