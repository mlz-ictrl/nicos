description = 'monochromator exchange setup'

group = 'lowlevel'

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    tran=device('nicos.devices.entangle.Motor',
                description='crystal translation',
                tangodevice=tango_base + 'exchange/tran',
                fmtstr='%.1f',
                requires={'level': 'admin'},
                ),
    inc=device('nicos.devices.entangle.Motor',
               description='crystal inclination',
               tangodevice=tango_base + 'exchange/inc',
               fmtstr='%.1f',
               requires={'level': 'admin'},
               ),
    cur=device('nicos.devices.entangle.Motor',
               description='crystal curved',
               tangodevice=tango_base + 'exchange/cur',
               fmtstr='%.2f',
               requires={'level': 'admin'},
               ),
    omgm=device('nicos.devices.entangle.Motor',
                description='crystal rotation',
                tangodevice=tango_base + 'exchange/omg',
                requires={'level': 'admin'},
                ),
)
