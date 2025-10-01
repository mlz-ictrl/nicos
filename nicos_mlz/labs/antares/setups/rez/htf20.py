description = 'High temperature furnace 20 - resistive heater'

group = 'optional'

tango_base = 'tango://htf20.antareslab:10000/box/eurotherm/'

devices = dict(
    TargetTemperature = device('nicos.devices.entangle.TemperatureController',
        description = 'Target temperature',
        tangodevice = tango_base + 'ctrl',
        precision = 2,
        fmtstr = '%.1f',
    ),
    Temperature = device('nicos.devices.entangle.Sensor',
        description = 'Actual temperature',
        tangodevice = tango_base + 'sens',
        fmtstr = '%.4f',
    ),
)

display_order = 40
