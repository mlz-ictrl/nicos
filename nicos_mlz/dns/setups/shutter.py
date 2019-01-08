# -*- coding: utf-8 -*-

description = 'DNS shutter digital in- and outputs'
group = 'lowlevel'

includes = ['reactor']

tango_base = 'tango://phys.dns.frm2:10000/dns/'

devices = dict(
    expshutter = device('nicos_mlz.jcns.devices.shutter.Shutter',
        description = 'Experiment Shutter',
        tangodevice = tango_base + 'fzjdp_digital/ExpShutter',
        mapping = dict(open = 1, closed = 2),
    ),
    nlashutter = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Status of NlaShutter',
        tangodevice = tango_base + 's7_digital/nla_shutter',
        mapping = dict(open = 1, closed = 2),
        lowlevel = True,
    ),
    fastshut = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Status of fastshutter',
        tangodevice = tango_base + 's7_digital/fast_shutter',
        mapping = dict(open = 1, closed = 2),
        lowlevel = True,
    ),
    enashut = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Shutter enable',
        tangodevice = tango_base + 's7_digital/shutter_enabled',
        mapping = dict(no = 0, yes = 1),
        lowlevel = True,
    ),
    cntrlshut = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Status of shutter control',
        tangodevice = tango_base + 's7_digital/shutter_control',
        mapping = dict(remote = 1, local = 0),
        lowlevel = True,
    ),
    keyswitch = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Status of shutter keyswitch',
        tangodevice = tango_base + 's7_digital/key_switch',
        mapping = dict(on = 1, off = 0),
        lowlevel = True,
    ),
    lamp = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Lamp restricted area',
        tangodevice = tango_base + 's7_digital/restricted_area_lamp',
        mapping = dict(on = 1, off = 0),
        lowlevel = True,
    ),
    lightgrid = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Status door',
        tangodevice = tango_base + 's7_digital/light_grid',
        mapping = dict(on = 1, off = 0),
        lowlevel = True,
    ),
)

extended = dict(
    representative = 'expshutter',
)
