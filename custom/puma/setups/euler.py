#  -*- coding: utf-8 -*-

description = 'Sample table for euler cradle'

group = 'optional'

includes = ['motorbus1', 'motorbus2', 'motorbus5']

devices = dict(
    st_echi= device('devices.vendor.ipc.Motor',
                    bus = 'motorbus2',
                    addr = 61,
                    slope = 200,
                    unit = 'deg',
                    abslimits = (-355, 355),
                    zerosteps = 500000,
                    lowlevel = True,
                   ),

    co_echi= device('devices.vendor.ipc.Coder',
                    bus = 'motorbus1',
                    addr = 132,
                    slope = -8192.5,
                    zerosteps = 5334445,
                    unit = 'deg',
                    lowlevel = True,
                   ),

    echi   = device('devices.generic.Axis',
                    motor = 'st_echi',
                    coder = 'co_echi',
                    obs = [],
                    precision = 0.01,
                    offset = -189.99926762282576,
                    fmtstr = '%.3f',
                    maxtries = 5,
                   ),


    st_ephi= device('devices.vendor.ipc.Motor',
                    bus = 'motorbus5',
                    addr = 84,
                    slope = -200,
                    unit = 'deg',
                    abslimits = (-180, 180),
                    zerosteps = 500000,
                    lowlevel = True,
                   ),

    co_ephi= device('devices.vendor.ipc.Coder',
                    bus = 'motorbus1',
                    addr = 133,
                    slope = 4096,
                    zerosteps = 9059075,
                    unit = 'deg',
                    circular = -360, # map values to -180..0..180 degree
                    lowlevel = True,
                   ),

    ephi   = device('devices.generic.Axis',
                    motor = 'st_ephi',
                    coder = 'co_ephi',
                    obs = [],
                    precision = 0.01,
                    offset = 0,
                    fmtstr = '%.3f',
                    maxtries = 5,
                   ),
)
