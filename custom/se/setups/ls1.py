description = 'LakeShore LS336 controller N1'

tango_base = 'tango://seplot.se.frm2:10000/se/%s' % setupname

devices = {
    'T_%s_control1' % setupname : device('nicos.devices.tango.TemperatureController',
                                  description = 'Loop 1',
                                  tangodevice = '%s/t_control1' % tango_base,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                  maxage = 7,
                                  abslimits = (0, 300),
                                 ),
    'T_%s_control2' % setupname : device('nicos.devices.tango.TemperatureController',
                                  description = 'Loop 2',
                                  tangodevice = '%s/t_control2' % tango_base,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                  maxage = 7,
                                  abslimits = (0, 300),
                                 ),
    'T_%s_1' % setupname : device('nicos.devices.tango.Sensor',
                                  description = 'Sensor 1',
                                  tangodevice = '%s/t_sensor1' % tango_base,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),
    'T_%s_2' % setupname : device('nicos.devices.tango.Sensor',
                                  description = 'Sensor 2',
                                  tangodevice = '%s/t_sensor2' % tango_base,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),
    'T_%s_3' % setupname : device('nicos.devices.tango.Sensor',
                                  description = 'Sensor 3',
                                  tangodevice = '%s/t_sensor3' % tango_base,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),
    'T_%s_4' % setupname : device('nicos.devices.tango.Sensor',
                                  description = 'Sensor 4',
                                  tangodevice = '%s/t_sensor4' % tango_base,
                                  unit = 'K',
                                  fmtstr = '%.3f',
                                 ),
}

startupcode = '''
'''
