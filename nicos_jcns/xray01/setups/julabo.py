# -*- coding: utf-8 -*-

description = 'Julabo temperature controller'
group = 'optional'

tango_base = 'tango://xray-se:10000/box/'

devices = dict(
    T_julabo = device('nicos.devices.entangle.TemperatureController',
        description = 'The regulated temperature',
        tangodevice = tango_base + 'julabo/control',
        abslimits = (5, 80),
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        timeout = 45 * 60.,
    ),
    T_julabo_bath = device('nicos.devices.entangle.Sensor',
        description = 'The bath temperature',
        tangodevice = tango_base + 'julabo/bath',
        lowlevel = False,
        unit = 'degC',
        fmtstr = '%.2f',
    ),
    T_julabo_external = device('nicos.devices.entangle.Sensor',
        description = 'The external sensor temperature',
        tangodevice = tango_base + 'julabo/extsensor',
        lowlevel = False,
        unit = 'degC',
        fmtstr = '%.2f',
    ),
    julabo_sensor = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Switch regulation sensor for Julabo',
        tangodevice = tango_base + 'julabo/external',
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
