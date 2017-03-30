# -*- coding: utf-8 -*-

description = 'Monitoring for MARIA setup'
group = 'basic'

tango_base = 'tango://localhost:10000/test'

devices = dict(
    maria_main_voltages = device(
        'emc.janitza_online.VectorInput',
        description = 'Voltage monitoring',
        tangodevice = tango_base + '/janitza_maria/voltages',
    ),
    maria_main_currents = device(
        'emc.janitza_online.VectorInput',
        description = 'Current monitoring',
        tangodevice = tango_base + '/janitza_maria/currents',
    ),
    maria_main_neutral = device(
        'emc.janitza_online.Neutral',
        description = 'Neutral current monitoring',
        tangodevice = tango_base + '/janitza_maria/neutral',
    ),
    maria_main_rcm = device(
        'emc.janitza_online.RCM',
        description = 'Residual current monitoring',
        tangodevice = tango_base + '/janitza_maria/rcm',
    ),
    maria_main_leakage = device(
        'emc.janitza_online.Leakage',
        description = 'Ground leakage monitoring',
        tangodevice = tango_base + '/janitza_maria/leakage',
    ),
    maria_main_thd = device(
        'emc.janitza_online.VectorInput',
        description = 'Total harmonic distortion monitoring',
        tangodevice = tango_base + '/janitza_maria/thd',
    ),
    maria_online = device(
        'emc.janitza_online.OnlineMonitor',
        description='Combination of all monitoring devices',
        voltages='maria_main_voltages',
        currents='maria_main_currents',
        neutral='maria_main_neutral',
        rcm='maria_main_rcm',
        leakage='maria_main_leakage',
        thd='maria_main_thd',
    ),
)
