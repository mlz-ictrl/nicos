description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements'
group = 'optional'

includes = []

devices = dict(
    M = device('mira.sr850.Amplifier',
                description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements',
                tacodevice = 'antares/rs232/sr830',
               ),
)

startupcode = '''
'''
