description = 'multimeter channels'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    coil_res = device('nicos.devices.tango.VectorInput',
        description = 'vacuum in coil 2 vessel',
        tangodevice = tango_base + 'dmm/ch',
        unit = 'Ohm',
        fmtstr = '%.3g',
        pollinterval = 10,
        maxage = 25,
    ),
)
