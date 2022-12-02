description = 'large beam limiter setup'

group = 'optional'

tango_base = 'tango://lahn:10000/astor/'

devices = dict(
    lbl_h=device('nicos.devices.entangle.Motor',
                 description='horizontal slit',
                 tangodevice=tango_base + 'lbl/h',
                 visibility=(),
                 ),
    lbl_v=device('nicos.devices.entangle.Motor',
                 description='vertical slit',
                 tangodevice=tango_base + 'lbl/v',
                 visibility=(),
                 ),
    lbl=device('nicos.devices.generic.TwoAxisSlit',
               description='beam limiter',
               horizontal='lbl_horizontal',
               vertical='lbl_vertical',
               requires={'level': 'admin'},
               ),
)
