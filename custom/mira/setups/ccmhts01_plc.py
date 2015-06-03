description = 'High-Tc superconducting magnet'

group = 'plugplay'

includes = ['alias_B']

taco_host = 'ccmhts01'

devices = dict(
    B_ccmhts01  = device('frm2.magnet.PLCMagnet',
                         description = 'magnetic field device',
                         tangodevice = 'tango://mira1.mira.frm2:10000/mira/htsplc/hts_B',
                         unit = 'T',
                         abslimits = (-2.2, 2.2),
                        ),
)

startupcode = '''
B.alias = B_ccmhts01
'''
