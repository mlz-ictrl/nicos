description = 'MIRA 0.5 T electromagnet'

group = 'plugplay'

includes = ['alias_B']

nethost = 'miramagnet'

devices = dict(
    I_plus   = device('mira.magnet.PhytronWorkaround',
                      tacodevice = '//%s/magnet/switch/on' % (nethost,),
                      mapping = {'off': 0, 'on': 1},
                      lowlevel = True,
                     ),
    I_minus  = device('devices.taco.NamedDigitalOutput',
                      tacodevice = '//%s/magnet/switch/pol' % (nethost,),
                      mapping = {'off': 0, 'on': 1},
                      lowlevel = True,
                     ),
    I        = device('devices.taco.CurrentSupply',
                      description = 'MIRA Helmholtz magnet current',
                      tacodevice = '//%s/magnet/ess/current' % (nethost,),
                      abslimits = (-250, 250),
                      fmtstr = '%.1f',
                     ),
    B_mira   = device('frm2.magnet.MiraMagnet',
                      currentsource = 'I',
                      plusswitch = 'I_plus',
                      minusswitch = 'I_minus',
                      description = 'MIRA magnetic field',
                      unit = 'T',
                      fmtstr = '%.4f',
                     ),
)

startupcode = '''
B.alias = B_mira
'''
