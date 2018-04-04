description = 'Safety detector system'

group = 'optional'

all_lowlevel = False  # or True

devices = dict(
    sds = device('nicos_mlz.refsans.devices.safedetectorsystem.SdsRatemeter',
        description = description,
        lowlevel = all_lowlevel,
        unit = 'cps',
    ),
)
