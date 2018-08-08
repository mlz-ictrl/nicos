description = 'Flexible temperature regulator'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    T_flex = device('nicos_mlz.kws3.devices.temperature.FlexRegulator',
        description = 'Flexible temperature regulation device',
        tangodevice = tango_base + 'flexreg/regulator',
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        timeout = 45 * 60.,
        dummy = tango_base + 'flexreg/dummy_in',
        configs = {
            'off':               (tango_base + 'flexreg/dummy_out', None),
            'julabo12-intern':   (tango_base + 'julabo12/control_int', None),
            'julabo12-extern':   (tango_base + 'julabo12/control_ext', None),
            'julabo12-mawi1':    (tango_base + 'julabo12/control_int', (tango_base + 'mawitherm/ch1', 10, 90, 30, 7, 2)),
            'julabo12-mawimean': (tango_base + 'julabo12/control_int', (tango_base + 'mawitherm/mean', 10, 90, 30, 7, 2)),
            'julabo22-intern':   (tango_base + 'julabo22/control_int', None),
            'julabo22-extern':   (tango_base + 'julabo22/control_ext', None),
            'julabo22-mawi1':    (tango_base + 'julabo22/control_int', (tango_base + 'mawitherm/ch1', 10, 90, 30, 7, 2)),
            'julabo22-mawimean': (tango_base + 'julabo22/control_int', (tango_base + 'mawitherm/mean', 10, 90, 30, 7, 2)),
        },
    ),
    T_flex_config = device('nicos_mlz.kws3.devices.temperature.ConfigParamDevice',
        description = 'Select the configuration for the flexible regulator',
        device = 'T_flex',
        parameter = 'config',
    ),
)

alias_config = {
    'T':  {'T_flex': 200},
    'Ts': {'T_flex': 200},
}
