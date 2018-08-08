description = 'Julabo temperature controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    T_julabo_1m_intern = device('nicos_mlz.kws1.devices.julabo.TemperatureController',
        description = 'Temperature regulation using internal bath',
        tangodevice = tango_base + 'julabo22/control_int',
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        timeout = 45 * 60.,
    ),
    T_julabo_1m_extern = device('nicos_mlz.kws1.devices.julabo.TemperatureController',
        description = 'Temperature regulation using external sensor',
        tangodevice = tango_base + 'julabo22/control_ext',
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        timeout = 45 * 60.,
    ),
)

alias_config = {
    'T':  {'T_julabo_1m_extern': 100, 'T_julabo_1m_intern': 90},
    'Ts': {'T_julabo_1m_extern': 100, 'T_julabo_1m_intern': 90},
}
