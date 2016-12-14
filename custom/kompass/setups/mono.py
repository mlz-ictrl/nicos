description = 'Monochromator tower devices'

group = 'lowlevel'

nethost = 'kompasshw.kompass.frm2'

devices = dict(
    # A1
    mth_m = device('devices.taco.Motor',
                   description = 'A1 motor',
                   tacodevice = '//%s/kompass/a1/motor' % nethost,
                   abslimits = (-10, 70),
                   fmtstr = '%.4f',
                   lowlevel = True,
                  ),
    mth_c = device('devices.taco.Coder',
                   description = 'A1 coder',
                   tacodevice = '//%s/kompass/a1/coder' % nethost,
                   fmtstr = '%.4f',
                   lowlevel = True,
                  ),
    mth = device('devices.generic.Axis',
                 description = 'mth (alias A1)',
                 motor = 'mth_m',
                 coder = 'mth_c',
                 fmtstr = '%.4f',
                 precision = 0.001,
                ),
)
