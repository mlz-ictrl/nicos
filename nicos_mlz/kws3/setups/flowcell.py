description = 'Flow cell'

group = 'optional'

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    flowcell_m = device('nicos.devices.tango.Sensor',
        description = 'balance readout',
        tangodevice = tango_base + 'sartorius/balance',
        unit = 'g',
        fmtstr = '%.3f',
    ),
    flowcell_sigma = device('nicos.devices.tango.Sensor',
        description = 'conductivity readout',
        tangodevice = tango_base + 'prema/input',
        unit = 'S',
        fmtstr = '%.3f',
    ),
)
