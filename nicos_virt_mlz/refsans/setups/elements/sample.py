description = 'Sample positions'

group = 'lowlevel'

devices = dict(
    d_last_slit_sample = device('nicos.devices.generic.ManualMove',
        description = 'distance last slit to samplecenter',
        abslimits = (0, 1000),
        fmtstr = '%.1f',
        unit = 'mm',
    ),
)
