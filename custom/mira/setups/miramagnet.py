description = 'MIRA 0.5 T electromagnet'
group = 'optional'

includes = ['base', 'alias_B']

devices = dict(
    I_plus   = device('devices.taco.DigitalOutput',
                      tacodevice = '//magnet2/magnet/switch/on',
                      lowlevel = True,
                     ),
    I_minus  = device('devices.taco.DigitalOutput',
                      tacodevice = '//magnet2/magnet/switch/pol',
                      lowlevel = True,
                     ),
    I        = device('devices.taco.CurrentSupply',
                      description = 'MIRA Helmholtz magnet current',
                      tacodevice = '//magnet2/magnet/ess/current',
                      abslimits = (-250, 250),
                      unit = 'A',
                      fmtstr = '%.1f',
                     ),
    B_mira   = device('frm2.magnet.MiraMagnet',
                      currentsource = 'I',
                      plusswitch = 'I_plus',
                      minusswitch = 'I_minus',
                      description = 'MIRA magnetic field',
                      # calibration from p6625_0000069{4-6}.dat
                      calibration = (0.000872603, -0.0242964, 0.0148907,
                                     0.0437158, 0.0157436),
                      abslimits = (-0.5, 0.5),
                      unit = 'T',
                     ),
)

startupcode = '''
B.alias = B_mira
'''
