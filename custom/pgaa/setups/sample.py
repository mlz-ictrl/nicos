description = 'sample table devices'

includes = []

nethost = 'pgaasrv.pgaa.frm2'

devices = dict(
    sensort = device('devices.taco.io.DigitalInput',
                     description =  ' sensor on top of tube',
                     tacodevice = '//pgaasrv.pgaa.frm2/pgaa/sample/tube_sensor_top',
                     lowlevel = True
                    ),
    sensorl = device('devices.taco.io.DigitalInput',
                     description =  ' sensor on bottom of tube',
                     tacodevice = '//pgaasrv.pgaa.frm2/pgaa/sample/tube_sensor_low',
                     lowlevel = True
                    ),

    usb485 = device('pgaa.samplechanger.TacoSerial',
                    lowlevel = True,
                    tacodevice = '//pgaasrv.pgaa.frm2/pgaa/rs232/usb485',
                    tacotimeout = 10,
                    comtries = 6,
                   ),

    samplemotor = device('pgaa.samplechanger.SampleMotor',
                         description = 'Motor rotating the Sample Chamber',
                         bus = 'usb485',
                         precision = 1,
                         fmtstr = '%.3f',
                         channel = 'X',
                         addr = 1,
                         slope = 1000,
                         abslimits = (0, 16),
                         unit = 'Pos',
                         idlecurrent = 0.1,
                         movecurrent = 1.41,
                         rampcurrent = 1.41,
                         microstep = 128,
                         speed = 0.2,
                         accel = 0.2,
                         sensor = 'sensort'
                        ),

    push = device('pgaa.samplechanger.SamplePusher',
                  description = 'Push sample up and down',
                  tacodevice = '//pgaasrv.pgaa.frm2/pgaa/sample/tube_press',
                  unit = '',
                  sensort = 'sensort',
                  sensorl = 'sensorl',
                  mapping = {'down': 1, 'up': 0},
                  motor = 'samplemotor'
                 ),
#   e1    = device('devices.taco.Coder',
#                  description = '',
#                  tacodevice = '//%s/pgaa/phytronixe/e1' % (nethost,),
#                  fmtstr = '%7.3f',
#                 ),
#   ellip = device('devices.taco.DigitalInput',
#                  description = '',
#                  tacodevice = '//%s/pgaa/pgai/ellip' % (nethost,),
#                 ),
#   ftube = device('devices.taco.DigitalInput',
#                  description = '',
#                  tacodevice = '//%s/pgaa/pgai/ftube' % (nethost,),
#                 ),
#   press1 = device('devices.taco.DigitalInput',
#                   description = '',
#                   tacodevice = '//%s/pgaa/pgai/press1' % (nethost,),
#                  ),
#   press2 = device('devices.taco.DigitalInput',
#                   description = '',
#                   tacodevice = '//%s/pgaa/pgai/press2' % (nethost,),
#                  ),
)
