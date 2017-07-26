description = 'Stressi specific high temperature furnace with cooling down ' \
              'option'

group = 'plugplay'

includes = ['alias_T']

nethost = setupname

plc_tango_base = 'tango://%s:10000/box/plc/_' % setupname

devices = {
    'T_%s' % setupname: device('nicos.devices.taco.TemperatureController',
                               description = 'The sample temperature',
                               tacodevice = '//%s/box/eurotherm/control' % nethost,
                               abslimits = (0, 2000),
                               unit = 'C',
                               fmtstr = '%.1f',
                              ),
    'T_sample_%s' % setupname: device('nicos.devices.taco.TemperatureSensor',
                                      description = 'The sample temperature '
                                                    'sensor',
                                      tacodevice = '//%s/box/eurotherm/sensora' % nethost,
                                      unit = 'C',
                                      fmtstr = '%.1f',
                                     ),
    'n2': device('nicos.devices.tango.NamedDigitalOutput',
                 description = 'N2 valve control',
                 tangodevice = plc_tango_base + 'gas1',
                 mapping = {'closed': 0, 'open': 1}
                ),
    'he': device('nicos.devices.tango.NamedDigitalOutput',
                 description = 'He valve control',
                 tangodevice = plc_tango_base + 'gas2',
                 mapping = {'closed': 0, 'open': 1}
                ),
    'lamps': device('nicos.devices.tango.NamedDigitalOutput',
                 description = 'Halogen lamps control',
                 tangodevice = plc_tango_base + 'onoff',
                 mapping = {'off': 0, 'on': 1}
                ),
    'water': device('nicos.devices.tango.NamedDigitalInput',
                    description = 'Cooling water status',
                    tangodevice = plc_tango_base + 'waterok',
                    mapping = {'failed': 0, 'ok': 1},
                   ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}
