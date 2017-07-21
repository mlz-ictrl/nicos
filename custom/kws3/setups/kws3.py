# -*- coding: utf-8 -*-

description = 'KWS-3 setup'
group = 'basic'

modules = ['nicos_mlz.kws3.commands']

includes = [
    'sample',
    'selector',
    'detector',
    'shutter',
    'polarizer',
    'daq',
    'vacuumsys',
]
