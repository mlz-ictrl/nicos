description = 'Julabo Presto temperature controller'

group = 'optional'

includes = ['alias_T']

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    T_control = device('devices.taco.TemperatureController',
                       description = 'The regulated temperature',
                       tacodevice = '//%s/sans1/julabo/control' % nethost,
                       abslimits = (-100, 250),
                       unit = 'C',
                       fmtstr = '%.2f',
                      ),
    T_intern = device('devices.taco.TemperatureSensor',
                      description = 'The internal sensor',
                      tacodevice = '//%s/sans1/julabo/intern' % nethost,
                      fmtstr = '%.2f',
                      unit = 'C',
                     ),
    T_extern = device('devices.taco.TemperatureSensor',
                      description = 'The external sensor',
                      tacodevice = '//%s/sans1/julabo/extern' % nethost,
                      fmtstr = '%.2f',
                      unit = 'C',
                     ),
)

alias_config = [
    ('T', 'T_control', 100),
    ('Ts', 'T_control', 100),
    ('Ts', 'T_extern', 90),
    ('Ts', 'T_intern', 80),
]
