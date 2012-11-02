#  -*- coding: utf-8 -*-

description = 'PUMA single detector'
group = 'lowlevel'

includes = ['motorbus1', 'motorbus6']

devices = dict(
    timer    = device('devices.taco.FRMTimerChannel',
                      tacodevice = 'puma/frmctr/at',
                      lowlevel = True),

    mon1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a1',
                      type = 'monitor',
                      lowlevel = True,
                      ),

    mon2     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a2',
                      type = 'monitor',
                      lowlevel = True,
                      ),

    det1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a3',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det2     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a4',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det3     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/b1',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det4     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/b2',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det5     = device('devices.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/b3',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det      = device('devices.taco.FRMDetector',
                      timer  = 'timer',
                      monitors = ['mon1', 'mon2'],
                      counters = ['det1', 'det2', 'det3', 'det4', 'det5'],
                      maxage = 1,
                      pollinterval = 1),


    st_sld = device('devices.vendor.ipc.Motor',
                    bus = 'motorbus6',
                    addr = 93,
                    slope = 4500,
                    unit = 'mm',
                    abslimits = (-0.1, 70.1),
                    zerosteps = 500000,
                    lowlevel = True,
                    ),
    co_sld = device('devices.vendor.ipc.Coder',
                    bus = 'motorbus1',
                    addr = 158,
                    slope = 37,
                    zerosteps = 68,
                    unit = 'mm',
                    lowlevel = True,
                    ),
    ds1    = device('devices.generic.Axis',
                    description = 'slit of detector opening',
                    motor = 'st_sld',
                    coder = 'co_sld',
                    obs = [],
                    precision = 0.2,
                    offset = 0,
                    fmtstr = '%.2f',
                    maxtries = 7,
                    ),

)
