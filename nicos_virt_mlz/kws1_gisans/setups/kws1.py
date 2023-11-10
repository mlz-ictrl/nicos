description = 'Virtual KWS-1 setup in GISANS mode'
group = 'basic'

modules = ['nicos_mlz.kws1.commands']

includes = [
    'sample',
    'selector',
    'detector',
    'shutter',
    'chopper',
    'collimation',
    'polarizer',
    'lenses',
    'daq',
]
