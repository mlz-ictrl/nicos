description = 'radial oscillating collimator setup'

group = 'optional'

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    rc=device('nicos.devices.entangle.Motor',
              description='curved',
              tangodevice=tango_base + 'rc/motor',
              fmtstr='%.2f',
              requires={'level': 'admin'},
              ),
)
