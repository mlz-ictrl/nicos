description = 'Sample positions'

group = 'lowlevel'

devices = dict(
    d_last_slit_sample = device('nicos.devices.generic.ManualMove',
        description = 'distance last slit to samplecenter max105mm at pivot 9',
        abslimits = (0, 1000),
        default = 100,
        fmtstr = '%.1f',
        unit = 'mm',
    ),
)
