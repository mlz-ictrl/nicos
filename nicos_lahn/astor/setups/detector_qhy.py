description = 'detector setup'

group = 'optional'

devices = dict(
    timer=device('nicos.devices.generic.VirtualTimer',
                 description='timer for the camera',
                 visibility=(),
                 ),
    qhy=device('nicos.devices.generic.VirtualImage',
               description='image for the camera',
               size=(1024, 1024),
               visibility=(),
               ),
    det=device('nicos.devices.generic.Detector',
               description='ccd camera',
               images=['qhy'],
               timers=['timer'],
               ),
)

startupcode = '''
SetDetectors(det)
'''
