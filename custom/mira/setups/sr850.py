description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements'
group = 'optional'

includes = ['base', 'ccr5']

devices = dict(
    M = device('mira.sr850.Amplifier',
               description = 'SR850 lock-in amplifier',
               tangodevice = 'tango://mira1.mira.frm2:10000/mira/sr850/io',
              ),
)

startupcode = '''
SetDetectors(M)
'''
