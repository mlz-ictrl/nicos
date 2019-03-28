description = 'POLI shutter devices'
group = 'lowlevel'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    ShutterOut = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_base + 's7_digital/shutter',
        lowlevel = True,
    ),
    ShutterIn = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_base + 's7_digital/shutter_in',
        lowlevel = True,
    ),
    Shutter = device('nicos_mlz.poli.devices.shutter.Shutter',
        description = 'POLI shutter control',
        data_out = 'ShutterOut',
        data_in = 'ShutterIn',
    ),
)
