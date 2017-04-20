description = 'REFSANS setup for LS340+rs232-5_07.res'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
#
## rs232server cryo exports
#
#    rs232_cryo = device('unknown_class:StringIO',
#                        description = 'Device test/rs232/cryo of Server rs232server cryo',
#                        tacodevice = '//%s/test/rs232/cryo' % nethost,
#                       ),

#
## lakeshore340server lakeshore01 exports
#
    ls340_control = device('devices.taco.TemperatureController',
                           description = 'Device test/ls340/control of Server lakeshore340server lakeshore01',
                           tacodevice = '//%s/test/ls340/control' % nethost,
                           abslimits = (0, 500),
                          ),

    ls340_sensora = device('devices.taco.TemperatureSensor',
                           description = 'Device test/ls340/sensora of Server lakeshore340server lakeshore01',
                           tacodevice = '//%s/test/ls340/sensora' % nethost,
                          ),

    ls340_sensorb = device('devices.taco.TemperatureSensor',
                           description = 'Device test/ls340/sensorb of Server lakeshore340server lakeshore01',
                           tacodevice = '//%s/test/ls340/sensorb' % nethost,
                          ),

    ls340_sensorc = device('devices.taco.TemperatureSensor',
                           description = 'Device test/ls340/sensorc of Server lakeshore340server lakeshore01',
                           tacodevice = '//%s/test/ls340/sensorc' % nethost,
                          ),

    ls340_sensord = device('devices.taco.TemperatureSensor',
                           description = 'Device test/ls340/sensord of Server lakeshore340server lakeshore01',
                           tacodevice = '//%s/test/ls340/sensord' % nethost,
                          ),

)
