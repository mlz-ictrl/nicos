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
)

