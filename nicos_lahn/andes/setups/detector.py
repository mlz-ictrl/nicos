description = 'detector setup'

group = 'lowlevel'

devices = dict(
    timer=device('nicos.devices.generic.VirtualTimer',
                 description='simulated timer',
                 visibility=(),
                 ),
    counter=device('nicos.devices.generic.VirtualCounter',
                   description='simulated counter',
                   type='counter',
                   visibility=(),
                   ),
    image=device('nicos.devices.generic.VirtualImage',
                 description='image data device',
                 visibility=(),
                 ),
    monitor=device('nicos.devices.generic.VirtualCounter',
                   description='simulated monitor',
                   type='monitor',
                   ),
    det=device('nicos.devices.generic.Detector',
               description='detector',
               counters=['counter'],
               images=['image'],
               monitors=['monitor'],
               timers=['timer'],
               ),
)

startupcode = '''
SetDetectors(det)
'''
