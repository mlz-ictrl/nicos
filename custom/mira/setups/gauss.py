includes = ['base']

devices = dict(
    mx = device('nicos.motor.Motor',
                tacodevice = 'mira/motor/x1',
                abslimits = (0, 250)),
    my = device('nicos.motor.Motor',
                tacodevice = 'mira/motor/x2',
                abslimits = (0, 90)),
    B  = device('nicos.mira.thm1176.THM',
                device = '/dev/usbtmc_THM1176'),
)

startupcode = '''
SetDetectors(B)
'''
