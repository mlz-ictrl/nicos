description = 'Safety detector system'

group = 'lowlevel'

all_lowlevel = False  # or True

devices = dict(
    sds = device('nicos_mlz.refsans.devices.gkssjson.SdsRatemeter',
        description = description,
        lowlevel = all_lowlevel,
        # valuekey = 'time',
        valuekey = 'mon_alarm',
        unit = 'cps',
    ),
)
