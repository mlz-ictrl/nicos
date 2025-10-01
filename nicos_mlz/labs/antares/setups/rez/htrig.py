description = 'High temperature furnace 20 - resistive heater'

group = 'optional'

tango_base_htf20 = 'tango://htf20.antareslab:10000/box/eurotherm/'
tango_base_rig = 'tango://localhost:10000/htrig/doli/'

devices = dict(
    Htf20Temperature = device('nicos.devices.entangle.TemperatureController',
        description = 'Target temperature',
        tangodevice = tango_base_htf20 + 'ctrl',
        precision = 2,
        fmtstr = '%.1f',
        pollinterval = 0.5,
    ),
    RigPosition = device('nicos.devices.entangle.Actuator',
        description = 'Position of the tensile rig',
        tangodevice = tango_base_rig + 'position',
        precision = 0.0001,
        fmtstr = '%.4f',
        pollinterval = 0.5,
    ),
    RigForce = device('nicos.devices.entangle.Actuator',
        description = 'Force of the tensile rig',
        tangodevice = tango_base_rig + 'force',
        precision = 2,
        fmtstr = '%.1f',
        pollinterval = 0.5,
    ),
    RigTime = device('nicos.devices.entangle.Sensor',
        description = 'Time elapsed since data recorded by Doli Test and Motion',
        tangodevice = tango_base_rig + 'time',
        pollinterval = 0.5,
    ),
)

display_order = 40
