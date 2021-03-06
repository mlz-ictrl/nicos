#  -*- coding: utf-8 -*-
description = 'Sample table'

#for goettingen use without physical axes

#includes = ['system',
#            'motorbus1', 'motorbus2', 'motorbus4', 'motorbus5', 'motorbus11']

includes = ['system']
devices = dict(
#    st_phi = device('nicos.devices.vendor.ipc.Motor',
#                    bus = 'motorbus4',
#                    addr = 53,
#                    slope = 400,
#                    unit = 'deg',
#                    abslimits = (-5, 114.1),
#                    zerosteps = 500000,
#                    #confbyte = ,
#                    #speed = ,
#                    #accel = ,
#                    #microstep = ,
#                    #startdelay = ,
#                    #stopdelay = ,
#                    #ramptype = ,
#                    lowlevel = True,
#                    ),
    st_phi = device('nicos.devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-355, 355),
                    ),
#    st_om  = device('nicos.devices.vendor.ipc.Motor',
#                    bus = 'motorbus2',
#                    addr = 58,
#                    slope = -400,
#                    unit = 'deg',
#                    abslimits = (1, 359),
#                    zerosteps = 500000,
#                    lowlevel = True,
#                    ),
    st_om  = device('nicos.devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-355, 355),
                    ),

#    st_sgx = device('nicos.devices.vendor.ipc.Motor',
#                    bus = 'motorbus11',
#                    addr = 64,
#                    slope = -3196,
#                    unit = 'deg',
#                    abslimits = (-15.6, 15.6),
#                    zerosteps = 500000,
#                    lowlevel = True,
#                    ),
    st_sgx = device('nicos.devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-15.6, 15.6),
                    ),

#    st_sgy = device('nicos.devices.vendor.ipc.Motor',
#                    bus = 'motorbus11',
#                    addr = 65,
#                    slope = -3196,
#                    unit = 'deg',
#                    abslimits = (-15.6, 15.6),
#                    zerosteps = 500000,
#                    lowlevel = True,
#                    ),
    st_sgy = device('nicos.devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-15.6, 15.6),
                    ),

#    st_stx = device('nicos.devices.vendor.ipc.Motor',
#                    bus = 'motorbus11',
#                    addr = 66,
#                    slope = -12750,
#                    unit = 'mm',
#                    abslimits = (-18, 13.5),
#                    zerosteps = 500000,
#                    lowlevel = True,
#                    ),
    st_stx = device('nicos.devices.generic.VirtualMotor',
                    unit = 'mm',
                    abslimits = (-18, 13.5),
                    ),

#    st_sty = device('nicos.devices.vendor.ipc.Motor',
#                    bus = 'motorbus11',
#                    addr = 67,
#                    slope = -13000,
#                    unit = 'mm',
#                    abslimits = (-18.1, 18.1),
#                    zerosteps = 500000,
#                    lowlevel = True,
#                    ),
    st_sty = device('nicos.devices.generic.VirtualMotor',
                    unit = 'mm',
                    abslimits = (-18, 13.5),
                    ),

#    st_stz = device('nicos.devices.vendor.ipc.Motor',
#                    bus = 'motorbus11',
#                    addr = 68,
#                    slope = -20000,
#                    unit = 'mm',
#                    abslimits = (-20, 20),
#                    zerosteps = 500000,
#                    lowlevel = True,
#                    ),
    st_stz = device('nicos.devices.generic.VirtualMotor',
                    unit = 'mm',
                    abslimits = (-20, 20),
                    ),

#    st_echi= device('nicos.devices.vendor.ipc.Motor',
#                    bus = 'motorbus2',
#                    addr = 61,
#                    slope = 200,
#                    unit = 'deg',
#                    abslimits = (-355, 355),
#                    zerosteps = 500000,
#                    lowlevel = True,
#                    ),
#    st_ephi= device('nicos.devices.vendor.ipc.Motor',
#                    bus = 'motorbus5',
#                    addr = 84,
#                    slope = -200,
#                    unit = 'deg',
#                    abslimits = (-180, 180),
#                    zerosteps = 500000,
#                    lowlevel = True,
#                    ),

    st_echi= device('nicos.devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-355, 355),
                    ),
    st_ephi= device('nicos.devices.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-180, 180),
                    ),

#    co_phi = device('nicos.devices.vendor.ipc.Coder',
#                    bus = 'motorbus1',
#                    addr = 128,
#                    slope = -186413.5111,
#                    zerosteps = 9392590,
#                    #confbyte = ,
#                    unit = 'deg',
#                    circular = -360, # map values to -180..0..180 degree
#                    lowlevel = True,
#                    ),
    co_phi  = device('nicos.devices.generic.VirtualCoder',
                    motor = 'st_phi',
                    lowlevel = True,
                    ),
#    co_om  = device('nicos.devices.vendor.ipc.Coder',
#                    bus = 'motorbus1',
#                    addr = 129,
#                    slope = -2912.7111,
#                    zerosteps = 206142,
#                    unit = 'deg',
#                    lowlevel = True,
#                    ),
    co_om  = device('nicos.devices.generic.VirtualCoder',
                    motor = 'st_om',
                    lowlevel = True,
                    ),

#    co_sgx = device('nicos.devices.vendor.ipc.Coder',
#                    bus = 'motorbus11',
#                    addr = 70,
#                    slope = -8192,
#                    zerosteps = 33466203,
#                    unit = 'deg',
#                    lowlevel = True,
#                    ),
    co_sgx  = device('nicos.devices.generic.VirtualCoder',
                    motor = 'st_sgx',
                    lowlevel = True,
                    ),

#    co_sgy = device('nicos.devices.vendor.ipc.Coder',
#                    bus = 'motorbus11',
#                    addr = 71,
#                    slope = -8192,
#                    zerosteps = 33553860,
#                    unit = 'deg',
#                    lowlevel = True,
#                    ),
    co_sgy  = device('nicos.devices.generic.VirtualCoder',
                    motor = 'st_sgy',
                    lowlevel = True,
                    ),

#    co_stx = device('nicos.devices.vendor.ipc.Coder',
#                    bus = 'motorbus11',
#                    addr = 74,
#                    slope = -154,
#                    zerosteps = 3798,
#                    unit = 'mm',
#                    lowlevel = True,
#                    ),
    co_stx  = device('nicos.devices.generic.VirtualCoder',
                    motor = 'st_stx',
                    lowlevel = True,
                    ),

#    co_sty = device('nicos.devices.vendor.ipc.Coder',
#                    bus = 'motorbus11',
#                    addr = 75,
#                    slope = -160,
#                    zerosteps = 4256,
#                    unit = 'mm',
#                    lowlevel = True,
#                    ),
    co_sty  = device('nicos.devices.generic.VirtualCoder',
                    motor = 'st_sty',
                    lowlevel = True,
                    ),

#    co_stz = device('nicos.devices.vendor.ipc.Coder',
#                    bus = 'motorbus11',
#                    addr = 76,
#                    slope = 155,
#                    zerosteps = 4055,
#                    unit = 'mm',
#                    lowlevel = True,
#                    ),
    co_stz  = device('nicos.devices.generic.VirtualCoder',
                    motor = 'st_stz',
                    lowlevel = True,
                    ),

#    co_echi= device('nicos.devices.vendor.ipc.Coder',
#                    bus = 'motorbus1',
#                    addr = 132,
#                    slope = -8192.5,
#                    zerosteps = 5334445,
#                    unit = 'deg',
#                    lowlevel = True,
#                    ),
#    co_ephi= device('nicos.devices.vendor.ipc.Coder',
#                    bus = 'motorbus1',
#                    addr = 133,
#                    slope = 4096,
#                    zerosteps = 9059075,
#                    unit = 'deg',
#                    circular = -360, # map values to -180..0..180 degree
#                    lowlevel = True,
#                    ),

    co_echi= device('nicos.devices.generic.VirtualCoder',
                    motor = 'st_echi',
                    lowlevel = True,
                    ),
    co_ephi= device('nicos.devices.generic.VirtualCoder',
                    motor = 'st_ephi',
                    lowlevel = True,
                    ),

    phi    = device('nicos.devices.generic.Axis',
                    motor = 'st_phi',
                    coder = 'co_phi',
                    obs = [],
                    precision = 0.005,
                    offset = 0.540,
                    maxtries = 5,
                    ),
    psi    = device('nicos.devices.generic.Axis',
                    motor = 'st_om',
                    coder = 'co_om',
                    obs = [],
                    precision = 0.005,
                    offset = -256.997,
                    fmtstr = '%.3f',
                    maxtries = 5,
                    ),
#    sth    = device('nicos_mlz.puma.devices.relaxis.PumaRelativeAxis',
#                    mov_ax = 'psi',
#                    relative_ax = 'phi',
#                    ),
    sgx    = device('nicos.devices.generic.Axis',
                    motor = 'st_sgx',
                    coder = 'co_sgx',
                    obs = [],
                    precision = 0.02,
                    offset = 0,
                    fmtstr = '%.3f',
                    maxtries = 5,
                    ),
    sgy    = device('nicos.devices.generic.Axis',
                    motor = 'st_sgy',
                    coder = 'co_sgy',
                    obs = [],
                    precision = 0.02,
                    offset = 0,
                    fmtstr = '%.3f',
                    maxtries = 5,
                    ),
    stx    = device('nicos.devices.generic.Axis',
                    motor = 'st_stx',
                    coder = 'co_stx',
                    obs = [],
                    precision = 0.05,
                    offset = 0.5,
                    fmtstr = '%.3f',
                    maxtries = 9,
                    ),
    sty    = device('nicos.devices.generic.Axis',
                    motor = 'st_sty',
                    coder = 'co_sty',
                    obs = [],
                    precision = 0.05,
                    offset = -0.15,
                    fmtstr = '%.3f',
                    maxtries = 9,
                    ),
    stz    = device('nicos.devices.generic.Axis',
                    motor = 'st_stz',
                    coder = 'co_stz',
                    obs = [],
                    precision = 0.1,
                    offset = 0,
                    fmtstr = '%.2f',
                    maxtries = 10,
                    ),
    echi   = device('nicos.devices.generic.Axis',
                    motor = 'st_echi',
                    coder = 'co_echi',
                    obs = [],
                    precision = 0.01,
                    offset = -189.99926762282576,
                    fmtstr = '%.3f',
                    maxtries = 5,
                    ),
    ephi   = device('nicos.devices.generic.Axis',
                    motor = 'st_ephi',
                    coder = 'co_ephi',
                    obs = [],
                    precision = 0.01,
                    offset = 0,
                    fmtstr = '%.3f',
                    maxtries = 5,
                    ),

)
