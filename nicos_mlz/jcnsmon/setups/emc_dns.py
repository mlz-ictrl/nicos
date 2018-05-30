# -*- coding: utf-8 -*-

description = 'Monitoring for DNS setup'
group = 'basic'

tango_base = 'tango://localhost:10000/test/'

devices = dict(
    dns_main_voltages = device('nicos_mlz.emc.devices.janitza_online.VectorInput',
        description = 'Voltage monitoring',
        tangodevice = tango_base + 'janitza_dns/voltages',
    ),
    dns_main_currents = device('nicos_mlz.emc.devices.janitza_online.VectorInput',
        description = 'Current monitoring',
        tangodevice = tango_base + 'janitza_dns/currents',
    ),
    dns_main_thd = device('nicos_mlz.emc.devices.janitza_online.VectorInput',
        description = 'Total harmonic distortion monitoring',
        tangodevice = tango_base + 'janitza_dns/thd',
    ),
    dns_online = device('nicos_mlz.emc.devices.janitza_online.OnlineMonitor',
        description = 'Combination of all monitoring devices',
        voltages = 'dns_main_voltages',
        currents = 'dns_main_currents',
        thd = 'dns_main_thd',
    ),
)
