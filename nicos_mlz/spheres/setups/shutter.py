# -*- coding: utf-8 -*-

description = 'setup for the shutter'

group = 'lowlevel'

includes = ['sps']

tangohost = 'phys.spheres.frm2'
shutter = 'tango://%s:10000/spheres/profibus/' % tangohost

devices = dict(
    shutter = device('nicos_mlz.spheres.devices.shutter.ShutterCluster',
        description = 'Display whether all the shutters leading to the sample '
        'are open',
        tangodevice = shutter + 'instrumentshutter',
        upstream = ['upstream_shut1', 'upstream_shut2', 'upstream_shut3'],
        chains = ['housing_chain1', 'housing_chain2', 'housing_chain_stairs'],
        door = 'door_closed_locked',
        mapping = {'open': 1,
                   'closed': 0},
        attachedmapping = {'closed': 0,
                           'open': 1},
        timeout = 5,
        shutterstatemapping = {
            0b000: 'closed: DNS, fast and 6-fold',
            0b001: 'closed: DNS and fast',
            0b010: 'closed: DNS and 6-fold',
            0b011: 'closed: DNS',
            0b100: 'closed: fast and 6-fold',
            0b101: 'closed: fast',
            0b110: 'closed: 6-fold',
        },
        chainstatemapping = {
            0b001: 'chain1 open',
            0b010: 'chain2 open',
            0b011: 'open chains: 1 and 2',
            0b100: 'chain_stairs open',
            0b101: 'open chains: 1 and stairs ',
            0b110: 'open chains: 2 and stairs',
            0b111: 'all chains open',
        }
    ),
)
