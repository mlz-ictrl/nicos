description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements'
group = 'optional'

includes = []

devices = dict(
    sr850 = device('mira.sr850.Amplifier',
                   description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements',
                   tacodevice = 'antares/network/sr830',
                  ),
)

startupcode = '''
'''
