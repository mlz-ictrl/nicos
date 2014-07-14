# -*- coding: utf-8 -*-

description = 'DNS shutter digital in- and outputs'

group = 'optional'

includes = ['reactor','nl6']

tango_host = 'tango://phys.dns.frm2:10000'

devices = dict(

    expshutter = device('dns.shutter.Shutter',
                        description = 'Experiment Shutter',
                        tangodevice = '%s/dns/FZJDP_Digital/ExpShutter' % tango_host,
                        mapping = dict(open=1, close=2),
                       ),

    nlashutter = device('devices.tango.NamedDigitalInput',
                        description = 'Status of NlaShutter',
                        tangodevice = '%s/dns/FZJDP_Digital/NlaShutter' % tango_host,
                        mapping = dict(open=1, close=2),
                        lowlevel = True,
                       ),

    fastshut   = device('devices.tango.NamedDigitalInput',
                        description = 'Status of fastshutter',
                        tangodevice = '%s/dns/FZJDP_Digital/Schnellschluss' % tango_host,
                        mapping = dict(open=1, close=2),
                        lowlevel = True,
                       ),

    enashut    = device('devices.tango.NamedDigitalInput',
                        description = 'Shutter enable',
                        tangodevice = '%s/dns/FZJDP_Digital/ShutterEnable' % tango_host,
                        mapping = dict(no=0, yes=1),
                        lowlevel = True,
                       ),

    cntrlshut  = device('devices.tango.NamedDigitalInput',
                        description = 'Status of shutter control',
                        tangodevice = '%s/dns/FZJDP_Digital/ShutterControl' % tango_host,
                        mapping = dict(remote=1, local=0),
                        lowlevel = True,
                       ),

    keyswitch  = device('devices.tango.NamedDigitalInput',
                        description = 'Status of shutter keyswitch',
                        tangodevice = '%s/dns/FZJDP_Digital/Keyswitch' % tango_host,
                        mapping = dict(on=1, off=0),
                        lowlevel = True,
                       ),

    lamp       = device('devices.tango.NamedDigitalInput',
                        description = 'Lamp restricted area',
                        tangodevice = '%s/dns/FZJDP_Digital/RestrictedArea' % tango_host,
                        mapping = dict(on=1, off=0),
                        lowlevel = True,
                       ),

    lightgrid  = device('devices.tango.NamedDigitalInput',
                        description = 'Status door',
                        tangodevice = '%s/dns/FZJDP_Digital/LightGrid' % tango_host,
                        mapping = dict(on=1, off=0),
                        lowlevel = True,
                       ),
)

startupcode = '''
'''
