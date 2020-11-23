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
    samplemotor = device('nicos.devices.tango.Motor',
        description = 'Motor rotating the Sample Chamber',
        tangodevice = tango_base + 'sample/motor',
        fmtstr = '%1.f',
        unit = 'Pos',
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
