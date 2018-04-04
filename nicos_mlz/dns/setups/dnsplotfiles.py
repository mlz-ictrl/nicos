# -*- coding: utf-8 -*-

description = 'Write files for each measurement'
group = 'optional'

sysconfig = dict(
    datasinks = ['DNSFileSaver', 'YAMLSaver'],
)

devices = dict(
    DNSFileSaver = device('nicos_mlz.dns.devices.dnsfileformat.DNSFileSink',
    ),
    YAMLSaver = device('nicos_mlz.dns.devices.yamlformat.YAMLFileSink',
    ),
)
