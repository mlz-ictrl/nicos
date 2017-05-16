description = 'Stressi specific high temperature furnace with cooling down ' \
              'option'

group = 'plugplay'

includes = ['alias_T']

nethost = setupname

devices = {
    'T_%s' % setupname: device('devices.taco.TemperatureController',
                               description = 'The sample temperature',
                               tacodevice = '//%s/box/eurotherm/control' % nethost,
                               abslimits = (0, 2000),
                               unit = 'C',
                               fmtstr = '%.1f',
                              ),
    'T_sample_%s' % setupname: device('devices.taco.TemperatureSensor',
                                      description = 'The sample temperature '
                                                    'sensor',
                                      tacodevice = '//%s/box/eurotherm/sensora' % nethost,
                                      unit = 'C',
                                      fmtstr = '%.1f',
                                     ),
    'n2': device('devices.taco.NamedDigitalOutput',
                 description = 'N2 valve control',
                 tacodevice = '//%s/box/plc/gas1' % nethost,
                 mapping = {'closed': 0, 'open': 1}
                ),
    'he': device('devices.taco.NamedDigitalOutput',
                 description = 'He valve control',
                 tacodevice = '//%s/box/plc/gas2' % nethost,
                 mapping = {'closed': 0, 'open': 1}
                ),
    'lamps': device('devices.taco.NamedDigitalOutput',
                 description = 'Halogen lamps control',
                 tacodevice = '//%s/box/plc/onoff' % nethost,
                 mapping = {'off': 0, 'on': 1}
                ),
    'water': device('devices.taco.NamedDigitalInput',
                    description = 'Cooling water status',
                    tacodevice = '//%s/box/plc/waterok' % nethost,
                    mapping = {'failed': 0, 'ok': 1},
                   ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
