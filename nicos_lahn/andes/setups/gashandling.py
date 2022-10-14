description = 'gas handling setup'

group = 'plugplay'

tango_base = 'tango://%s:10000/box/' % setupname

devices = dict(
    controller=device('nicos.devices.entangle.TemperatureController',
                      description='PID controller',
                      tangodevice=tango_base + 'temperatureController/regulator',
                      ),
    sensor=device('nicos.devices.entangle.Sensor',
                  description='temperature sensor',
                  tangodevice=tango_base + 'temperatureController/sensor',
                  ),
)

startupcode = '''
read()
'''
