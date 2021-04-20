description = 'Dilatometer'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://stressictrl.stressi.frm2:10000/stressi/dilato/'

devices = {
    'Ts_dil': device('nicos.devices.entangle.Sensor',
        description = 'The sample temperature',
        tangodevice = tango_base + 'temp',
        pollinterval = 2.0,
    ),
    'dil_time': device('nicos.devices.entangle.Sensor',
        description = 'Time since start of dilatometer data collection',
        tangodevice = tango_base + 'time',
        pollinterval = 2.0,
    ),
    'dil_dl': device('nicos.devices.entangle.Sensor',
        description = 'The length change',
        tangodevice = tango_base + 'dl',
        pollinterval = 2.0,
    ),
    'dil_force': device('nicos.devices.entangle.Sensor',
        description = 'The force of the dilatometer',
        tangodevice = tango_base + 'force',
    ),
    'dil_set_temp': device('nicos.devices.entangle.Sensor',
        description = 'The sample setpoint temperature',
        tangodevice = tango_base + 'set_temp',
    ),
    'dil_power': device('nicos.devices.entangle.Sensor',
        description = 'The HF heating power',
        tangodevice = tango_base + 'heaterpower',
        pollinterval = 2.0,
    ),
    'dil_trigger': device('nicos.devices.entangle.DigitalOutput',
        description = 'Trigger for skipping to the next dilatometer measurement segment',
        tangodevice = tango_base + 'trigger',
    ),
}

alias_config = {
    'Ts': {'Ts_dil': 100},
}
