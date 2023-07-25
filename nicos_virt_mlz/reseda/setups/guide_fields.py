description = 'Guide fields'
group = 'lowlevel'
display_order = 20

devices = {
    'gf%i' % i: device('nicos.devices.generic.ManualMove',
        description = 'Guide field %i' % i,
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 119, # maxage should not be a multiple of pollinterval!
        unit = 'A',
        abslimits = (0, 5),
        # precision = 0.005,
    ) for i in ([0, 1, 2] + list(range(4, 11)))
}
