description = 'THM1176 gaussmeter'

includes = ['base']

devices = dict(
    B  = device('nicos.mira.thm1176.THM',
                device = '/dev/usbtmc_THM1176'),
)

startupcode = '''
AddDetector(B)
'''
