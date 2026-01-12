description = 'Be filter'

group = 'lowlevel'
tango_base = 'tango://tango:8001/v6/befilter/'

devices = dict(
    high_be=device('nicos.devices.entangle.Motor',
                   description='vertical movement',
                   tangodevice=tango_base + 'high',
                   unit='mm',
                   ),
)
