description = 'Lift and pitch of deflector and flight tube'

display_order = 40

pvprefix = 'SQ:AMOR:mmac1:'

devices = dict(
    ltz_r = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Lift (z translation) of deflector & flight tube',
        motorpv = pvprefix + 'ltz',
        errormsgpv = pvprefix + 'ltz-MsgTxt',
        visibility = ('devlist', 'metadata', 'namespace'),
        precision = .1,
        can_disable = True,
        auto_enable = False,
    ),
    lom_r = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Tilt (pitch) of deflector & flight tube',
        motorpv = pvprefix + 'lom',
        errormsgpv = pvprefix + 'lom-MsgTxt',
        visibility = ('devlist', 'metadata', 'namespace'),
        precision = .01,
        can_disable = True,
        auto_enable = False,
    ),
)
alias_config = {'lom': {'lom_r': 10}, 'ltz': {'ltz_r': 10}}
