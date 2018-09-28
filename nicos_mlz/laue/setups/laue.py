# -*- coding: utf-8 -*-
description = 'laue basic setup'

group = 'basic'

modules = [
    'nicos.commands.utility',
    'nicos_mlz.laue.lauecommands'
]

devices = dict(
)

includes = ['detector', 'kappa', 'reactor', 'slits', 'shutter']
