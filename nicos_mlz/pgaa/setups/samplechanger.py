description = 'sample table devices'

group = 'lowlevel'

excludes = ['sampletable']

tango_base = 'tango://pgaahw.pgaa.frm2.tum.de:10000/pgaa/'

devices = dict(
    sensort = device('nicos.devices.entangle.DigitalInput',
        description = 'sensor at the top of tube',
        tangodevice = tango_base + 'sample/tube_sensor_top',
        visibility = ()
    ),
    sensorl = device('nicos.devices.entangle.DigitalInput',
        description = 'sensor at the bottom of tube',
        tangodevice = tango_base + 'sample/tube_sensor_low',
        visibility = ()
    ),
    samplemotor = device('nicos.devices.entangle.Motor',
        description = 'Motor rotating the Sample Chamber',
        tangodevice = tango_base + 'sample/motor',
        fmtstr = '%.1f',
        unit = 'Pos',
        visibility = (),
    ),
    pushactuator = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Push device actuator',
        tangodevice = tango_base + 'sample/tube_press',
        mapping = {'down': 1,
                   'up': 0},
        visibility = (),
    ),
    push = device('nicos_mlz.pgaa.devices.SamplePusher',
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
