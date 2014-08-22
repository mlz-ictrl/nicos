description = 'MIRA 0.5 T electromagnet'
group = 'optional'

includes = ['base', 'alias_B']

devices = dict(
    I_plus   = device('mira.magnet.PhytronWorkaround',
                      tacodevice = '//magnet2/magnet/switch/on',
                      mapping = {'off': 0, 'on': 1},
                      lowlevel = True),
    I_minus  = device('devices.taco.NamedDigitalOutput',
                      tacodevice = '//magnet2/magnet/switch/pol',
                      mapping = {'off': 0, 'on': 1},
                      lowlevel=True),
    I        = device('devices.taco.CurrentSupply',
                      description = 'MIRA Helmholtz magnet current',
                      tacodevice = '//magnet2/magnet/ess/current',
                      abslimits = (-250, 250),
                      fmtstr = '%.1f'),
    B_mira   = device('frm2.magnet.MiraMagnet',
                      currentsource = 'I',
                      plusswitch = 'I_plus',
                      minusswitch = 'I_minus',
                      description = 'MIRA magnetic field',
                      abslimits = (-0.5, 0.5),
                      unit = 'T',
                      fmtstr = "%.4f"),
)

startupcode = '''
B.alias = B_mira
'''
