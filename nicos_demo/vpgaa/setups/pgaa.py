description = 'virtual PGAA experiment setup'

group = 'basic'

sysconfig = dict(
    datasinks = ['sink']
)

includes = [
    'system',
    # 'reactor',
    # 'nl4b',
    'pressure',
    'samplechanger',
    'pilz',
    'detector',
    'collimation',
]

devices = dict(
    sink = device('nicos_mlz.pgaa.devices.PGAASink',
        det1 = '_60p',
        det2 = 'LEGe',
        vac = 'chamber_pressure',
    ),
)

startupcode = '''
# SetDetectors(det)
SetEnvironment()
printinfo("============================================================")
printinfo("Welcome to the NICOS PGAA demo setup.")
printinfo("============================================================")
'''
