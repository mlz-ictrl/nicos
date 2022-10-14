description = 'connecting arms setup for the other modes of operation'

group = 'lowlevel'

excludes = ['connecting_arms']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    lms=device('nicos.devices.generic.ManualMove',
               description='sample table arm translation',
               abslimits=(1600, 2800),
               unit='mm',
               default=1600,
               fmtstr='%.2f',
               requires={'level': 'admin'},
               ),
    lsd=device('nicos.devices.generic.ManualMove',
               description='detector arm translation',
               abslimits=(1100, 1100),
               unit='mm',
               default=1100,
               fmtstr='%.2f',
               requires={'level': 'admin'},
               ),
    stt=device('nicos.devices.entangle.Motor',
               description='2 theta axis moving detector arm',
               tangodevice=tango_base + 'arms/stt',
               fmtstr='%.2f',
               requires={'level': 'admin'},
               userlimits=(15, 160),
               ),
)

startupcode = '''
maw(stt, 15)
'''
