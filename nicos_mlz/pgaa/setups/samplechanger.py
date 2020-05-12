description = 'sample table devices'

group = 'lowlevel'

excludes = ['sampletable']

tango_base = 'tango://pgaahw.pgaa.frm2:10000/pgaa/'

devices = dict(
    sensort = device('nicos.devices.tango.DigitalInput',
        description = 'sensor at the top of tube',
        tangodevice = tango_base + 'sample/tube_sensor_top',
        lowlevel = True
    ),
    sensorl = device('nicos.devices.tango.DigitalInput',
        description = 'sensor at the bottom of tube',
        tangodevice = tango_base + 'sample/tube_sensor_low',
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
        lowlevel = True,
    ),
    pushactuator = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Push device actuator',
        tangodevice = tango_base + 'sample/tube_press',
        mapping = {'down': 1,
                   'up': 0},
        lowlevel = True,
    ),
    push = device('nicos_mlz.pgaa.devices.sampledevices.SamplePusher',
        description = 'Push sample up and down',
        unit = '',
        actuator = 'pushactuator',
        sensort = 'sensort',
        sensorl = 'sensorl',
    ),
    sc = device('nicos_mlz.pgaa.devices.SampleChanger',
        description = 'The sample changer',
        motor = 'samplemotor',
        push = 'push',
    ),
)
