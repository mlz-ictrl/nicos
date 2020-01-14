description = 'Safety detector system'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

code_base = instrument_values['code_base']

devices = dict(
    sds = device(code_base + 'gkssjson.SdsRatemeter',
        description = description,
        lowlevel = False,
        # valuekey = 'time',
        valuekey = 'mon_alarm',
        unit = 'cps',
    ),
)
