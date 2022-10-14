description = 'connecting arms setup for tension scanner'

group = 'lowlevel'

excludes = ['connecting_arms_2']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    lms=device('nicos.devices.generic.ManualMove',
               description='sample table arm translation',
               abslimits=(1600, 2200),
               unit='mm',
               default=1600,
               fmtstr='%.2f',
               requires={'level': 'admin'},
               ),
    lsd=device('nicos.devices.generic.ManualMove',
               description='detector arm translation',
               abslimits=(900, 1500),
               unit='mm',
               default=900,
               fmtstr='%.2f',
               requires={'level': 'admin'},
               ),
    stt=device('nicos.devices.entangle.Motor',
               description='2 theta axis moving detector arm',
               tangodevice=tango_base + 'arms/stt',
               fmtstr='%.2f',
               requires={'level': 'admin'},
               userlimits=(65, 110),
               ),
)

startupcode = '''
maw(stt, 65)
'''
