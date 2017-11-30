description = "dimension of sample"

group = 'lowlevel'

devices = dict(
    width = device('nicos.devices.generic.ManualMove',
        description = 'width of sample lateral',
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
