description = "dimension of sample"

group = 'lowlevel'
# group = 'optional'

devices = dict(
    width = device('nicos.devices.generic.ManualMove',
        description = 'with of sample lateral',
        abslimits = (0, 100),
        fmtstr = '%.1f',
        unit = 'mm',
    ),
    length = device('nicos.devices.generic.ManualMove',
        description = 'length of sample in beam',
        abslimits = (0, 100),
        fmtstr = '%.1f',
        unit = 'mm',
    ),
)
