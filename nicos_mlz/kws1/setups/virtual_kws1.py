# -*- coding: utf-8 -*-

description = 'Fully virtual KWS-1 setup'
group = 'basic'

modules = ['nicos_mlz.kws1.commands']

includes = [
    'virtual_sample',
    'virtual_selector',
    'virtual_detector',
    'virtual_shutter',
    'virtual_chopper',
    'virtual_collimation',
    'virtual_polarizer',
    'virtual_lenses',
    'virtual_daq',
]
