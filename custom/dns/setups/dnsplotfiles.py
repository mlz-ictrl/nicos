# -*- coding: utf-8 -*-

description = "Write files for each measurement"
group = "optional"

sysconfig = dict(
    datasinks = ['DNSFileSaver', 'YAMLSaver'],
)

devices = dict(
    DNSFileSaver = device('dns.dnsfileformat.DNSFileSink',
                          lowlevel = True,
                         ),
    YAMLSaver    = device('dns.yamlformat.YAMLFileSink',
                          lowlevel = True,
                         ),
)
