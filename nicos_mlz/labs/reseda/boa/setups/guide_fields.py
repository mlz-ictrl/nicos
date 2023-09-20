description = 'Guide fields'
group = 'lowlevel'
display_order = 20

tango_base = 'tango://%s:10000/reseda/' % configdata('gconfigs.tango_host')

devices = {
    'gf%i' % i: device('nicos.devices.entangle.PowerSupply',
        description = 'Guide field %i' % i,
        tangodevice = tango_base + 'coil/gf%i' % i,
        fmtstr = '%.3f',
        tangotimeout = 30.0,
        pollinterval = 60,
        maxage = 119, # maxage should not be a multiple of pollinterval!
        unit = 'A',
        precision = 0.005,
    # ) for i in ([0, 1, 2, 4, 5, 6, 7, 8, 9, 10])
    ) for i in ([2, 8, 9])
}
