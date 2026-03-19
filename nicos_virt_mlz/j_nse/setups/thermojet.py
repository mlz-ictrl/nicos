description = 'ThermoJet sample environment'
group = 'optional'

devices = dict(
    T_thermojet = device('nicos.devices.generic.virtual.VirtualMotor',
        description = 'ThermoJet temperature',
        userlimits = (0, 100),
        abslimits = (0, 100),
        speed = 20.,
        unit = 'degC',
        fmtstr = '%.3g',
        pollinterval = 0.5,
    ),
)
