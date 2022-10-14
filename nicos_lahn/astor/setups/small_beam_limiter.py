description = 'small beam limiter setup'

group = 'lowlevel'

tango_base = 'tango://lahn:10000/astor/'

devices = dict(
    sbl_h=device('nicos.devices.entangle.Motor',
                 description='horizontal slit',
                 tangodevice=tango_base + 'sbl/h',
                 visibility=(),
                 ),
    sbl_v=device('nicos.devices.entangle.Motor',
                 description='vertical slit',
                 tangodevice=tango_base + 'sbl/v',
                 visibility=(),
                 ),
    sbl=device('nicos.devices.generic.TwoAxisSlit',
               description='beam limiter',
               horizontal='sbl_h',
               vertical='sbl_v',
               requires={'level': 'admin'},
               ),
)
