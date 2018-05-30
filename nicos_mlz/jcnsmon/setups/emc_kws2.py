# -*- coding: utf-8 -*-

description = 'Monitoring for KWS2 setup'
group = 'basic'

tango_base = 'tango://localhost:10000/test/'

devices = dict(
    kws2_main_voltages = device('nicos_mlz.emc.devices.janitza_online.VectorInput',
        description = 'Voltage monitoring',
        tangodevice = tango_base + 'janitza_kws2/voltages',
    ),
    kws2_main_currents = device('nicos_mlz.emc.devices.janitza_online.VectorInput',
        description = 'Current monitoring',
        tangodevice = tango_base + 'janitza_kws2/currents',
    ),
    kws2_main_neutral = device('nicos_mlz.emc.devices.janitza_online.Neutral',
        description = 'Neutral current monitoring',
        tangodevice = tango_base + 'janitza_kws2/neutral',
    ),
    kws2_main_rcm = device('nicos_mlz.emc.devices.janitza_online.RCM',
        description = 'Residual current monitoring',
        tangodevice = tango_base + 'janitza_kws2/rcm',
    ),
    kws2_main_leakage = device('nicos_mlz.emc.devices.janitza_online.Leakage',
        description = 'Ground leakage monitoring',
        tangodevice = tango_base + 'janitza_kws2/leakage',
    ),
    kws2_main_thd = device('nicos_mlz.emc.devices.janitza_online.VectorInput',
        description = 'Total harmonic distortion monitoring',
        tangodevice = tango_base + 'janitza_kws2/thd',
    ),
    kws2_online = device('nicos_mlz.emc.devices.janitza_online.OnlineMonitor',
        description = 'Combination of all monitoring devices',
        voltages = 'kws2_main_voltages',
        currents = 'kws2_main_currents',
        neutral = 'kws2_main_neutral',
        rcm = 'kws2_main_rcm',
        leakage = 'kws2_main_leakage',
        thd = 'kws2_main_thd',
    ),
)
