description = 'lens switching devices'
group = 'lowlevel'
display_order = 75

excludes = ['virtual_lenses']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    lenses = device('nicos_mlz.kws1.devices.lens.Lenses',
        description = 'high-level lenses device',
        io = 'lens_io',
    ),
    lens_set = device('nicos.devices.entangle.DigitalOutput',
        tangodevice = tango_base + 'sps/lens_write',
        fmtstr = '%#x',
        visibility = (),
    ),
    lens_in = device('nicos.devices.entangle.DigitalInput',
        tangodevice = tango_base + 'sps/lens_in',
        fmtstr = '%#x',
        visibility = (),
    ),
    lens_out = device('nicos.devices.entangle.DigitalInput',
        tangodevice = tango_base + 'sps/lens_out',
        fmtstr = '%#x',
        visibility = (),
    ),
    lens_sync = device('nicos.devices.entangle.DigitalOutput',
        tangodevice = tango_base + 'sps/sync_bit',
        fmtstr = '%#x',
        visibility = (),
    ),
    lens_io = device('nicos_mlz.kws1.devices.lens.LensControl',
        description = 'lens I/O device',
        output = 'lens_set',
        input_in = 'lens_in',
        input_out = 'lens_out',
        sync_bit = 'lens_sync',
        timeout = 30.0,
        visibility = (),
    ),
)

extended = dict(
    representative = 'lenses',
)
