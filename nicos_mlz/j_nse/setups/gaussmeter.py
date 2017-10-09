description = 'THM1176 gaussmeter probe for magnetic field measurements'
group = 'optional'

devices = dict(
    Bf  = device('nicos_mlz.mira.devices.thm1176.THM',
                 description = 'THM 1176 gaussmeter',
                 device = '/dev/usbtmc0',
                ),
)

startupcode = '''
AddDetector(Bf)
'''
