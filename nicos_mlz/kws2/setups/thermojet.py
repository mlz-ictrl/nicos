description = 'Thermojet airflow controller'

group = 'optional'

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    T_thermojet = device('nicos.devices.entangle.TemperatureController',
        description = 'The regulated temperature',
        tangodevice = tango_base + 'thermojet/control',
        abslimits = (10, 50),
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        timeout = 45 * 60.,
    ),
    flow_thermojet = device('nicos.devices.entangle.AnalogOutput',
        description = 'Airflow through the nozzle',
        tangodevice = tango_base + 'thermojet/airflow',
    ),
)

extended = dict(
    representative = 'T_thermojet',
)
