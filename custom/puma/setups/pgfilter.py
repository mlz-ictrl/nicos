#  -*- coding: utf-8 -*-

description = 'PG filter'

includes = ['system', 'motorbus6', 'motorbus8']

devices = dict(
    fpg_sw    = device('devices.vendor.ipc.Input',
                       bus = 'motorbus8',
                       addr = 103,
                       first = 14,
                       last = 15,
                       lowlevel = True,
                       ),
    fpg_set   = device('devices.vendor.ipc.Output',
                       bus = 'motorbus8',
                       addr = 114,
                       first = 2,
                       last = 2,
                       lowlevel = True,
                       ),
    fpg_press = device('devices.vendor.ipc.Input',
                       bus = 'motorbus8',
                       addr = 103,
                       first = 11,
                       last = 11,
                       lowlevel = True,
                       ),

    st_hof    = device('devices.vendor.ipc.Motor',
                       bus = 'motorbus6',
                       addr = 91,
                       slope = -359.57,
                       unit = 'deg',
                       abslimits = (-4.2, 4.2),
                       zerosteps = 500000,
                       lowlevel = True,
                       ),
    hof       = device('devices.generic.Axis',
                       motor = 'st_hof',
                       coder = 'st_hof',
                       obs = [],
                       precision = 0.01,  # not used
                       offset = 0,
                       fmtstr = '%.3f',
                       ),

    fpg       = device('puma.filter.PumaFilter',
                       motor = 'hof',
                       io_status = 'fpg_sw',
                       io_set = 'fpg_set',
                       io_press = 'fpg_press',
                       justpos = 0.9,
                       material = 'graphite',
                       width = 5,
                       height = 10,
                       thickness = 5,
                       ),
)
