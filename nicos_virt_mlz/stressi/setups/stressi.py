description = 'Virtual STRESS-SPEC setup with sample table'

group = 'basic'

includes = [
    'system', 'sampletable', 'monochromator', 'detector', 'primaryslit',
    'slits', 'reactor'
]

excludes = ['robot']

sysconfig = dict(
        datasinks = ['caresssink'],
)

