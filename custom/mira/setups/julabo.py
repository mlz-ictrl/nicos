description = 'Julabo "bio oven"'
group = 'optional'

includes = ['alias_T']

tango_url = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    T_julabo = device('devices.tango.TemperatureController',
                      description = 'temperature regulation',
                      tangodevice = tango_url + 'julabo/temp',
                      pollinterval = 0.7,
                      maxage = 2,
                      abslimits = (0, 100),
                      unit = 'degC',
                     ),
)

startupcode = '''
T.alias = T_julabo
Ts.alias = T_julabo
'''
