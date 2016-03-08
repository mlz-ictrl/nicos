description = 'LakeShore 340 cryo controller'

includes = ['alias_T']

group = 'optional'

devices = dict(
    T_ls340   = device('devices.taco.TemperatureController',
                       description = 'PANDA lakeshore controller',
                       tacodevice = 'panda/ls340/control',
                       maxage = 2,
                       abslimits = (0, 300),
                      ),
    T_ls340_A = device('devices.taco.TemperatureSensor',
                       description = 'PANDA lakeshore Sensor A',
                       tacodevice = 'panda/ls340/sensora',
                       maxage = 2,
                      ),
    T_ls340_B = device('devices.taco.TemperatureSensor',
                       description = 'PANDA lakeshore Sensor B',
                       tacodevice = 'panda/ls340/sensorb',
                       maxage = 2,
                      ),
    T_ls340_C = device('devices.taco.TemperatureSensor',
                       description = 'PANDA lakeshore Sensor C',
                       tacodevice = 'panda/ls340/sensorc',
                       maxage = 2,
                      ),
    T_ls340_D = device('devices.taco.TemperatureSensor',
                       description = 'PANDA lakeshore Sensor D',
                       tacodevice = 'panda/ls340/sensord',
                       maxage = 2,
                      ),


#~   cc_compressor_wut = device('panda.wechsler.Beckhoff',
                             #~ host='compressor.panda.frm2',
                             #~ description='WUT-IO device to switch compressors on/off',
                             #~ addr=1,
                             #~ lowlevel=True,
                            #~ ),
#~   cc_compressor_switch = device('panda.satbox.SatBox',
                                #~ bus='cc_compressor_wut',
                                #~ description='Temporary HACK to switch CC-compressor on (1) or off(0)',
                                #~ widths=[1],
                                #~ fmtstr='%d',
                                #~ unit='mm',
                               #~ ),

)

alias_config = {
    'T': {'T_ls340': 200},
    'Ts': {'T_ls340_B': 100, 'T_ls340_A': 90, 'T_ls340_C': 80, 'T_ls340_D': 70},
}
