include = 'stdsystem'

devices = dict(
    dev1=device('test.utils.TestDevice',
                unit='mm',
                abslimits=(-5, 5),
                maxage=0.0,  # no caching!
                target = 1,
                ),
    dev2=device('test.utils.TestDevice',
                unit='mm',
                abslimits=(-5, 5),
                maxage=0.0,  # no caching!
                target = 2,
                ),
    dev3=device('test.utils.TestDevice',
                unit='mm',
                abslimits=(-5, 5),
                maxage=0.0,  # no caching!
                target = 3,
                ),
    dev4=device('test.utils.TestDevice',
                unit='mm',
                abslimits=(-5, 5),
                maxage=0.0,  # no caching!
                target = 4,
                ),
    dev5=device('nicos.core.device.Device'),
)
