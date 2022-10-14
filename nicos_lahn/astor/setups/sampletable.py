description = 'sample table setup'

group = 'optional'

tango_base = 'tango://lahn:10000/astor/'

devices = dict(
    x=device('nicos.devices.entangle.Motor',
             description='translation x',
             tangodevice=tango_base + 'sampletable/x',
             fmtstr='%d',
             ),
    y=device('nicos.devices.entangle.Motor',
             description='translation y',
             tangodevice=tango_base + 'sampletable/y',
             fmtstr='%.d',
             ),
    z=device('nicos.devices.entangle.Motor',
             description='translation z',
             tangodevice=tango_base + 'sampletable/z',
             fmtstr='%d',
             ),
    phi=device('nicos.devices.entangle.Motor',
               description='rotation phi',
               tangodevice=tango_base + 'sampletable/phi',
               fmtstr='%d',
               ),
)
