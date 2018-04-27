description = 'Oil-Julabo temperature controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    T_oiljulabo = device('nicos_mlz.kws1.devices.julabo.TemperatureController',
        description = 'The regulated temperature',
        tangodevice = tango_base + 'oiljulabo/control',
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        timeout = 45 * 60.,
    ),
)

alias_config = {
    'T':  {'T_oiljulabo': 100},
    'Ts': {'T_oiljulabo': 100},
}

extended = dict(
    representative = 'T_oiljulabo',
)
