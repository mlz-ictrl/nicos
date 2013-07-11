# -*- coding: utf-8 -*-

description = """temperature monitoring with FRM-II CCR and
weather measuring stations provided by LMU"""
group = "optional"

includes = ["meteo"]

nethost = 'cryostream.taco.frm2'

devices = dict(

    sensor_a = device('devices.taco.TemperatureSensor',
                      tacodevice = '//%s/ccr/ls336/sensora' % (nethost, ),
                      unit = 'C',
                      fmtstr = '%.1f'),

    sensor_b = device('devices.taco.TemperatureSensor',
                      tacodevice = '//%s/ccr/ls336/sensorb' % (nethost, ),
                      unit = 'C',
                      fmtstr = '%.1f'),

    sensor_c = device('devices.taco.TemperatureSensor',
                      tacodevice = '//%s/ccr/ls336/sensorc' % (nethost, ),
                      unit = 'C',
                      fmtstr = '%.1f'),

    sensor_d = device('devices.taco.TemperatureSensor',
                      tacodevice = '//%s/ccr/ls336/sensord' % (nethost, ),
                      unit = 'C',
                      fmtstr = '%.1f'),

)
