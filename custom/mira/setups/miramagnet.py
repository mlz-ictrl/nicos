description = 'MIRA 0.5 T electromagnet'
group = 'optional'

includes = ['alias_B']

devices = dict(
    I_plus   = device('mira.magnet.PhytronWorkaround',
                      tacodevice = '//miramagnet/magnet/switch/on',
                      mapping = {'off': 0, 'on': 1},
                      lowlevel = True,
                     ),
    I_minus  = device('devices.taco.NamedDigitalOutput',
                      tacodevice = '//miramagnet/magnet/switch/pol',
                      mapping = {'off': 0, 'on': 1},
                      lowlevel = True,
                     ),
    I        = device('devices.taco.CurrentSupply',
                      description = 'MIRA Helmholtz magnet current',
                      tacodevice = '//miramagnet/magnet/ess/current',
                      abslimits = (0, 250),
                      fmtstr = '%.1f',
                     ),
    B_mira   = device('frm2.magnet.MiraMagnet',
                      currentsource = 'I',
                      plusswitch = 'I_plus',
                      minusswitch = 'I_minus',
                      description = 'MIRA magnetic field',
                      # no abslimits: they are automatically determined from I
                      unit = 'T',
                      fmtstr = "%.4f",
                     ),
)

startupcode = '''
B.alias = B_mira
'''
