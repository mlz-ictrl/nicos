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
    d_last_slit_sample = device('nicos.devices.generic.ManualMove',
        description = 'distance last slit to samplecenter',
        abslimits = (0,1000),
        fmtstr = '%.1f',
        unit = 'mm',
    ),
    last_slit = device('nicos.devices.generic.ManualSwitch',
        description = 'with is the last slit',
        states = ['b2', 'b3'],
        fmtstr = '%s',
    ),
)
