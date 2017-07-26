description = 'THM1176 gaussmeter probe for magnetic field measurements'
group = 'optional'

includes = ['base']

devices = dict(
    Bf  = device('nicos_mlz.mira.devices.thm1176.THM',
                 description = 'THM 1176 gaussmeter',
                 device = '/dev/usbtmc_THM1176',
                ),
)

startupcode = '''
AddDetector(Bf)
'''
