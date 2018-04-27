description = 'Helmholtz field coil'

group = 'optional'

includes = ['alias_B']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    I_helmholtz = device('nicos.devices.tango.PowerSupply',
        description = 'Current in coils',
        tangodevice = tango_base + 'gesupply/ps2',
        unit = 'A',
        fmtstr = '%.2f',
    ),
    B_helmholtz = device('nicos.devices.generic.CalibratedMagnet',
        currentsource = 'I_helmholtz',
        description = 'Magnet field',
        unit = 'T',
        fmtstr = '%.5f',
        calibration = (
            0.0032507550, # slope 0.003255221(old)
            0,
            0,
            0,
            0
        )
    ),
)

alias_config = {
    'B':  {'B_helmholtz': 100},
}

extended = dict(
    representative = 'B_helmholtz',
)
