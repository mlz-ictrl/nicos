description = 'Water-Julabo temperature controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    T_julabo = device('nicos_mlz.kws1.devices.julabo.TemperatureController',
        description = 'The regulated temperature',
        tangodevice = tango_base + 'waterjulabo/control',
        abslimits = (5, 80),
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        timeout = 45 * 60.,
    ),
    T_julabo_bath = device('nicos.devices.entangle.Sensor',
        description = 'The bath temperature',
        tangodevice = tango_base + 'waterjulabo/bath',
        lowlevel = True,
        unit = 'degC',
        fmtstr = '%.2f',
    ),
    T_julabo_external = device('nicos.devices.entangle.Sensor',
        description = 'The external sensor temperature',
        tangodevice = tango_base + 'waterjulabo/extsensor',
        lowlevel = True,
        unit = 'degC',
        fmtstr = '%.2f',
    ),
    julabo_sensor = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Switch regulation sensor for Julabo',
        tangodevice = tango_base + 'waterjulabo/external',
        mapping = dict(extern=1, intern=0),
    ),
)

alias_config = {
    'T':  {'T_julabo': 100},
    'Ts': {'T_julabo': 100},
}

extended = dict(
    representative = 'T_julabo',
)
