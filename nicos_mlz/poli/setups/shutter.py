description = 'POLI shutter devices'
group = 'lowlevel'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    ShutterControl = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_base + 'fzjdp_digital/Shutter',
        lowlevel = True,
    ),
    Shutter = device('nicos_mlz.poli.devices.shutter.Shutter',
        description = 'POLI shutter control',
        io = 'ShutterControl',
    ),
)
