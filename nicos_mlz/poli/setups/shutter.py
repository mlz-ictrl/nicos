description = 'POLI shutter devices'
group = 'lowlevel'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    ShutterOut = device('nicos.devices.entangle.DigitalOutput',
        tangodevice = tango_base + 's7_io/shutter',
        visibility = (),
    ),
    ShutterIn = device('nicos.devices.entangle.DigitalOutput',
        tangodevice = tango_base + 's7_io/shutter_in',
        visibility = (),
    ),
    Shutter = device('nicos_mlz.poli.devices.shutter.Shutter',
        description = 'POLI shutter control',
        data_out = 'ShutterOut',
        data_in = 'ShutterIn',
    ),
)
