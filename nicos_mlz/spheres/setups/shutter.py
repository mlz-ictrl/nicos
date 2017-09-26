# -*- coding: utf-8 -*-

description = 'setup for the shutter'

group = 'optional'

includes = ['sps']

tangohost = 'phys.spheres.frm2'
shutter = 'tango://%s:10000/spheres/profibus/' % tangohost

devices = dict(
    shutter = device('nicos_mlz.spheres.devices.shutter.ShutterCluster',
        description = 'Display whether all the shutters leading to the sample '
        'are open',
        tangodevice = shutter + 'instrumentshutter',
        upstream = ['upstream_shut1', 'upstream_shut2', 'upstream_shut3'],
        mapping = {'open': 1,
                   'close': 0},
        attachedmapping = {'closed': 0,
                           'open': 1},
        timeout = 5,
        statusmapping = {
            0: 'closed: DNS, fast and 6-fold',
            1: 'closed: DNS and fast',
            2: 'closed: DNS and 6-fold',
            3: 'closed: DNS',
            4: 'closed: fast and 6-fold',
            5: 'closed: fast',
            6: 'closed: 6-fold',
        },
    ),
)
