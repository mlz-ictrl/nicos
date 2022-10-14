description = 'sample table setup'

group = 'optional'

excludes = ['goniometer']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    x=device('nicos.devices.entangle.Motor',
             description='sample table translation x',
             tangodevice=tango_base + 'sampletable/x',
             fmtstr='%.2f',
             ),
    y=device('nicos.devices.entangle.Motor',
             description='sample table translation y',
             tangodevice=tango_base + 'sampletable/y',
             fmtstr='%.2f',
             ),
    z=device('nicos.devices.entangle.Motor',
             description='sample table translation z',
             tangodevice=tango_base + 'sampletable/z',
             fmtstr='%.2f',
             ),
    phi=device('nicos.devices.entangle.Motor',
               description='sample table rotation phi',
               tangodevice=tango_base + 'sampletable/phi',
               ),
)
