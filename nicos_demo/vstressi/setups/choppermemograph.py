description = 'memograph readout for the chopper cooling system'

includes = []

group = 'lowlevel'

system = 'chopper'

devices = {
    't_in_%s_cooling' % system[:2]: device('nicos.devices.generic.VirtualMotor',
        description = 'inlet temperature %s cooling' % system,
        fmtstr = '%.1f',
        abslimits = (0, 40),
        warnlimits = (None, 17.5),  # -1 no lower value
        curvalue = 14.3,
        unit = 'degC',
    ),
    't_out_%s_cooling' % system[:2]: device('nicos.devices.generic.VirtualMotor',
        description = 'outlet temperature %s cooling' % system,
        fmtstr = '%.1f',
        abslimits = (0, 60),
        curvalue = 19.2,
        unit = 'degC',
    ),
    'p_in_%s_cooling' % system[:2]: device('nicos.devices.generic.VirtualMotor',
        description = 'inlet pressure %s cooling' % system,
        fmtstr = '%.1f',
        abslimits = (0, 10),
        curvalue = 5.0,
        unit = 'bar',
    ),
    'p_out_%s_cooling' % system[:2]: device('nicos.devices.generic.VirtualMotor',
        description = 'outlet pressure %s cooling' % system,
        fmtstr = '%.1f',
        curvalue = 2.1,
        abslimits = (0, 10),
        unit = 'bar',
    ),
    'flow_in_%s_cooling' % system[:2]: device('nicos.devices.generic.VirtualMotor',
        description = 'inlet flow %s cooling' % system,
        fmtstr = '%.1f',
        curvalue = 7.0,
        warnlimits = (0.2, None),  # 100 no upper value
        abslimits = (0, 100),
        unit = 'l/min',
    ),
    'flow_out_%s_cooling' % system[:2]: device('nicos.devices.generic.VirtualMotor',
        description = 'outlet flow %s cooling' % system,
        fmtstr = '%.1f',
        curvalue = 6.9,
        abslimits = (0, 100),
        unit = 'l/min',
    ),
    'leak_%s_cooling' % system[:2]: device('nicos.devices.generic.VirtualMotor',
        description = 'leakage %s cooling' % system,
        fmtstr = '%.1f',
        warnlimits = (None, 1),  # -1 no lower value
        curvalue = 0.1,
        abslimits = (0, 100),
        unit = 'l/min',
    ),
    'power_%s_cooling' % system[:2]: device('nicos.devices.generic.VirtualMotor',
        description = 'cooling %s cooling' % system,
        fmtstr = '%.1f',
        abslimits = (0, 5),
        curvalue = 2.2,
        unit = 'kW',
    ),
}
