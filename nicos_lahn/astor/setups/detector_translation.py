description = 'detector table setup'

group = 'lowlevel'

tango_base = 'tango://lahn:10000/astor/'

devices = dict(
    dtx=device('nicos.devices.entangle.Motor',
               description='translation x',
               tangodevice=tango_base + 'dt/x',
               ),
    dty=device('nicos.devices.entangle.Motor',
               description='translation y',
               tangodevice=tango_base + 'dt/y',
               ),
)
