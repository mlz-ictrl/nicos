description = 'STRESS-SPEC setup with sample table'

group = 'basic'

includes = [
    'system',
    'reactor',
    'monochromator',
    'slits',
    'primaryslit',
    'sampletable',
    'vdetector',
]

sysconfig = dict(
    datasinks = ['caresssink'],
)
