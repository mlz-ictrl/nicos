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
    nlashutter = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Status of NlaShutter',
        tangodevice = tango_base + 's7_io/nla_shutter',
        mapping = dict(open = 1, closed = 2),
        visibility = (),
    ),
    fastshut = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Status of fastshutter',
        tangodevice = tango_base + 's7_io/fast_shutter',
        mapping = dict(open = 1, closed = 2),
        visibility = (),
    ),
    enashut = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Shutter enable',
        tangodevice = tango_base + 's7_io/shutter_enabled',
        mapping = dict(no = 0, yes = 1),
        visibility = (),
    ),
    cntrlshut = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Status of shutter control',
        tangodevice = tango_base + 's7_io/shutter_control',
        mapping = dict(remote = 1, local = 0),
        visibility = (),
    ),
    keyswitch = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Status of shutter key switch',
        tangodevice = tango_base + 's7_io/key_switch',
        mapping = dict(on = 1, off = 0),
        visibility = (),
    ),
    lamp = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Lamp restricted area',
        tangodevice = tango_base + 's7_io/restricted_area_lamp',
        mapping = dict(on = 1, off = 0),
        visibility = (),
    ),
    lightgrid = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Status door',
        tangodevice = tango_base + 's7_io/light_grid',
        mapping = dict(on = 1, off = 0),
        visibility = (),
    ),
)

extended = dict(
    representative = 'expshutter',
)
