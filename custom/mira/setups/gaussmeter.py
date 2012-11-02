description = 'THM1176 gaussmeter probe for magnetic field measurements'
group = 'optional'

includes = ['base']

devices = dict(
    Bf  = device('mira.thm1176.THM',
                 device = '/dev/usbtmc_THM1176'),
)

startupcode = '''
AddDetector(Bf)
'''
