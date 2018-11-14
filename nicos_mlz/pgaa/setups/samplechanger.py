description = 'sample table devices'

group = 'lowlevel'

excludes = ['sampletable']

nethost = 'pgaasrv.pgaa.frm2'
tango_base = 'tango://pgaahw.pgaa.frm2:10000/pgaa/'

devices = dict(
    sensort = device('nicos.devices.taco.io.DigitalInput',
        description = ' sensor on top of tube',
        tacodevice = '//pgaasrv.pgaa.frm2/pgaa/sample/tube_sensor_top',
        lowlevel = True
    ),
    sensorl = device('nicos.devices.taco.io.DigitalInput',
        description = ' sensor on bottom of tube',
        tacodevice = '//pgaasrv.pgaa.frm2/pgaa/sample/tube_sensor_low',
        lowlevel = True
    ),
    usb485 = device('nicos_mlz.panda.devices.mcc2.TangoSerial',
        lowlevel = True,
        tangodevice = tango_base + 'rs232/usb485',
        comtries = 6,
    ),
    samplemotor = device('nicos_mlz.pgaa.devices.sampledevices.SampleMotor',
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
        sensor = 'sensort',
        lowlevel = True,
    ),
    push = device('nicos_mlz.pgaa.devices.sampledevices.SamplePusher',
        description = 'Push sample up and down',
        tacodevice = '//pgaasrv.pgaa.frm2/pgaa/sample/tube_press',
        unit = '',
        sensort = 'sensort',
        sensorl = 'sensorl',
        mapping = {'down': 1,
                   'up': 0},
        motor = 'samplemotor'
    ),
    sc = device('nicos_mlz.pgaa.devices.SampleChanger',
        description = 'The sample changer',
        motor = 'samplemotor',
        push = 'push',
    ),
)
