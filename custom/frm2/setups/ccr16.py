description = 'FRM-II CCR box with LakeShore LS336 controller'

group = 'optional'

includes = ['alias_T']

nethost = 'ccr16'

devices = dict(
    'T_%s_stick' % (nethost, ) : device('nicos.taco.TemperatureController',
                                        description = 'The control device to the sample',
                                        tacodevice = '//%s/ccr/ls336/control2' % (nethost, ),
                                        userlimits = (0, 600),
                                        abslimits = (0, 600),
                                        unit = 'K',
                                        fmtstr = '%.3f',
                                        pollinterval = 5,
                                        maxage = 20,
                                       ),

    'T_%s_tube' % (nethost, ) : device('nicos.taco.TemperatureController',
                                       description = 'The control device of the tube',
                                       tacodevice = '//%s/ccr/ls336/control1' % (nethost, ),
                                       userlimits = (0, 400),
                                       abslimits = (0, 400),
                                       unit = 'K',
                                       fmtstr = '%.3f',
                                       pollinterval = 5,
                                       maxage = 20,
                                      ),

    'T_%s_A' % (nethost,) : device('nicos.taco.TemperatureSensor',
                                   description = 'Temperature at the tube',
                                   tacodevice = '//%s/ccr/ls336/sensora' % (nethost, ),
                                   unit = 'K',
                                   fmtstr = '%.3f'
                                   pollinterval = 5,
                                   maxage = 20,
                                  ),

    'T_%s_B' % (nethost,) : device('nicos.taco.TemperatureSensor',
                                   description = 'Temperature at the tube',
                                   tacodevice = '//%s/ccr/ls336/sensorb' % (nethost, ),
                                   unit = 'K',
                                   fmtstr = '%.3f',
                                   pollinterval = 5,
                                   maxage = 20,
                                  ),

    'T_%s_C' % (nethost,) : device('nicos.taco.TemperatureSensor',
                                   description = 'Temperature at the sample stick',
                                   tacodevice = '//%s/ccr/ls336/sensorc' % (nethost, ),
                                   unit = 'K',
                                   fmtstr = '%.3f',
                                   pollinterval = 5,
                                   maxage = 20,
                                  ),

    'T_%s_D' % (nethost,) : device('nicos.taco.TemperatureSensor',
                                   description = 'Temperature at the sample stick',
                                   tacodevice = '//%s/ccr/ls336/sensord' % (nethost, ),
                                   unit = 'K',
                                   fmtstr = '%.3f',
                                   pollinterval = 5,
                                   maxage = 20,
                                  ),

    '%s_compressor_switch' % (nethost,) : device('nicos.taco.DigitalOutput',
                                                 description = 'Switch for the compressor',
                                                 tacodevice = '//%s/ccr/plc/on' % (nethost, )
                                                ),

    '%_gas_set' % (nethost,) : device('nicos.taco.DigitalOutput',
                                      description = 'Switch for the gas valve',
                                      lowlevel = True,
                                      tacodevice = '//%s/ccr/plc/gas' % (nethost, )
                                     ),

    '%s_gas_read' % (nethost,) : device('nicos.taco.DigitalInput',
                                        description = 'Read back of the gas valve state',
                                        lowlevel = True,
                                        tacodevice = '//%s/ccr/plc/fbgas' % (nethost, )
                                       ),

    '%s_gas_switch' % (nethost,) : device('nicos.frm2.ccr.DigitalOutput',
                                          description = 'Gas valve switch',
                                          write = '%s_gas_set' % (nethost,),
                                          feedback = '%s_gas_read' % (nethost,),
                                         ),

    '%s_vacuum_set' % (nethost,) : device('nicos.taco.DigitalOutput',
                                          description = 'Switch for the vacuum valve',
                                          lowlevel = True,
                                          tacodevice = '//%s/ccr/plc/vacuum' % (nethost, )
                                         ),

    '%s_vacuum_read' % (nethost,) : device('nicos.taco.DigitalInput',
                                           description = 'Read back of the vacuum valve state',
                                           lowlevel = True,
                                           tacodevice = '//%s/ccr/plc/fbvacuum' % (nethost, )
                                         ),

    '%s_vaccum_switch' % (nethost,) : device('nicos.frm2.ccr.DigitalOutput',
                                             description = 'Vacuum valve switch',
                                             write = '%s_vacuum_set' % (nethost,),
                                             feedback = '%s_vacuum_read' % (nethost,),
                                            ),

    '%s_p1' % (nethost,) = device('nicos.taco.AnalogInput',
                                  description = 'Pressure in sample space',
                                  tacodevice = '//%s/ccr/plc/p1' % (nethost, )
                                  pollinterval = 15,
                                  maxage = 20,
                                  unit = "mbar",
                                 ),

    '%s_p2' % (nethost,) = device('nicos.taco.AnalogInput',
                                  description = 'Pressure in the vacuum chamber',
                                  tacodevice = '//%s/ccr/plc/p2' % (nethost, )
                                  pollinterval = 15,
                                  maxage = 20,
                                  unit = "mbar",
                                 ),
)

startupcode = """
T.alias = T_%s_stick
Ts.alias = T_%s_D
AddEnvironment(T, Ts)
""" % (nethost, nethost, )
