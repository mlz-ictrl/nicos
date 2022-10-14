description = 'sample table goniometer setup'

group = 'optional'

excludes = ['sampletable']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    x=device('nicos.devices.entangle.Motor',
             description='sample table translation x',
             tangodevice=tango_base + 'goniometer/x',
             ),
    y=device('nicos.devices.entangle.Motor',
             description='sample table translation y',
             tangodevice=tango_base + 'goniometer/y',
             ),
    z=device('nicos.devices.entangle.Motor',
             description='sample table translation z',
             tangodevice=tango_base + 'goniometer/z',
             ),
    phi=device('nicos.devices.entangle.Motor',
               description='sample table rotation phi',
               tangodevice=tango_base + 'goniometer/phi',
               ),
    chi=device('nicos.devices.entangle.Motor',
               description='sample table rotation chi',
               tangodevice=tango_base + 'goniometer/chi',
               ),
)
