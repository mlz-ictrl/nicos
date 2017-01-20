description = 'STRESS-SPEC setup with sample table'

group = 'basic'

includes = ['system', 'mux', 'sampletable', 'monochromator', 'detector',
            'primaryslit', 'slits', 'reactor']

excludes = ['robot']

sysconfig = dict(
    datasinks = ['caresssink'],
)

devices = dict(
)
