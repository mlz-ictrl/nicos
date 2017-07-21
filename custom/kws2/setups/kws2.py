# -*- coding: utf-8 -*-

description = 'KWS-2 setup'
group = 'basic'

modules = ['nicos_mlz.kws1.commands']

includes = [
    'sample',
    'selector',
    'detector',
    'shutter',
    'chopper',
    'collimation',
    'lenses',
    'virtual_polarizer',
    'daq',
]
