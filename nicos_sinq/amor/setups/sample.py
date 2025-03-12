description = 'Sample devices in the SINQ AMOR.'

display_order = 50

pvprefix = 'SQ:AMOR:mmac1:'

devices = dict(
    som = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample omega rotation',
        motorpv = pvprefix + 'som',
        precision = .01,
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    soz = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample z lift (below omega and chi rotation)',
        motorpv = pvprefix + 'soz',
        precision = .01,
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    sch = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample chi rotation',
        motorpv = pvprefix + 'sch',
        precision = .01,
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    sph = device('nicos_sinq.devices.epics.motor.SinqMotor',
       description = 'Sample phi rotation',
       motorpv = pvprefix + 'sph',
       precision = .01,
       visibility = (),
    ),
    temperature = device('nicos.core.device.DeviceAlias',
       description = 'Sample temperature',
       alias = 'sim_temp',
       visibility = (),
    ),
    magnetic_field = device('nicos.core.device.DeviceAlias',
       description = 'Magnetic field at sample',
       alias = 'sim_field',
       visibility = (),
    ),
)
