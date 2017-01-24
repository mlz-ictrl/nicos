# -*- coding: utf-8 -*-

description = 'Spodi neutron guide'

group = 'lowlevel'

includes = []

taco_base = '//nguidectrl.spodi.frm2/spodi/'


devices = dict(
    p1_nguide = device('devices.taco.AnalogInput',
                     description = 'Pressure 1',
                     tacodevice = taco_base + 'center/center_0',
                     fmtstr = '%.2f',
                     maxage = 65,
                     pollinterval = 30,
                    ),
    p2_nguide = device('devices.taco.AnalogInput',
                     description = 'Pressure 2',
                     tacodevice = taco_base + 'center/center_1',
                     fmtstr = '%.2f',
                     maxage = 65,
                     pollinterval = 30,
                    ),
    p3_nguide = device('devices.taco.AnalogInput',
                     description = 'Pressure 3',
                     tacodevice = taco_base + 'center/center_2',
                     fmtstr = '%.2f',
                     maxage = 65,
                     pollinterval = 30,
                    ),
    o2_nguide = device('devices.taco.AnalogInput',
                     description = 'O2',
                     tacodevice = taco_base + 'greisinger/o2',
                     fmtstr = '%.2f',
                     maxage = 65,
                     pollinterval = 30,
                    ),
    o2part_nguide = device('devices.taco.AnalogInput',
                     description = 'O2 part',
                     tacodevice = taco_base + 'greisinger/o2part',
                     fmtstr = '%.2f',
                     maxage = 65,
                     pollinterval = 30,
                    ),
    T_nguide = device('devices.taco.AnalogInput',
                     description = 'Temperature',
                     tacodevice = taco_base + 'greisinger/temp',
                     fmtstr = '%.2f',
                     maxage = 65,
                     pollinterval = 30,
                    ),
)

display_order = 100
startupcode = '''
'''
