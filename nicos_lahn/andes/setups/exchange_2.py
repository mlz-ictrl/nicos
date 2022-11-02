description = 'monochromator exchange setup'

group = 'lowlevel'

includes = ['monoblock']

excludes = ['exchange', 'exchange_3']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    meZ=device('nicos.devices.entangle.Motor',
               description='exchange translation',
               tangodevice=tango_base + 'exchange/z',
               userlimits=(74,76),
               fmtstr='%.1f',
               visibility=(),
               ),
    crystal=device('nicos_lahn.andes.devices.monoexchange.Exchange',
                   description='exchange',
                   mb=['mb%d' % i for i in range(1, 4)],
                   moveable='meZ',
                   mapping={
                       'Ge': 75,
                   },
                   precision=0.1,
                   requires={'level': 'admin'},
                   ),
    omgm=device('nicos.devices.entangle.Motor',
                description='crystal rotation',
                tangodevice=tango_base + 'exchange/omg',
                requires={'level': 'admin'},
                ),
)

startupcode = '''
maw(crystal, 'Ge')
'''
