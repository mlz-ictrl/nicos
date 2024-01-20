description = 'Sample devices in the SINQ AMOR.'

display_order = 50

pvprefix = 'SQ:AMOR:mmac1:'

devices = dict(
    som = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Sample omega rotation',
        motorpv = pvprefix + 'som',
        errormsgpv = pvprefix + 'som-MsgTxt',
        precision = .01,
        can_disable = True,
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    soz = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Sample z lift (below omega and chi rotation)',
        motorpv = pvprefix + 'soz',
        errormsgpv = pvprefix + 'soz-MsgTxt',
        precision = .01,
        can_disable = True,
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    sch = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Sample chi rotation',
        motorpv = pvprefix + 'sch',
        errormsgpv = pvprefix + 'sch-MsgTxt',
        precision = .01,
        can_disable = True,
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    sph = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Sample phi rotation',
        motorpv = pvprefix + 'sph',
        errormsgpv = pvprefix + 'sph-MsgTxt',
        precision = .01,
        can_disable = True,
        visibility = (),
    ),
    sim_temp = device('nicos.devices.generic.manual.ManualMove',
        description = 'Simulated temperature',
        unit = 'K',
        abslimits = (-1000, 10000),
        default = -9999,
        visibility = (),
    ),
    sim_field = device('nicos.devices.generic.manual.ManualMove',
        description = 'Simulated magnetic field',
        unit = 'A',
        abslimits = (-1000, 10000),
        default = -9999,
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
alias_config = {
    'temperature': {
        'sim_temp': 10
    },
    'magnetic_field': {
        'sim_field': 10
    }
}
