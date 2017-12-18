description = 'FRM II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s' % setupname: device('nicos.devices.tango.TemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base + 'eurotherm/ctrl',
        abslimits = (0, 2000),
        precision = 0.1,
        fmtstr = '%.3f',
        unit = 'C',
    ),
    '%s_watertemp' % setupname: device('nicos.devices.tango.Sensor',
        description = 'Cooling water temperature',
        tangodevice = tango_base + 'plc/_water_temp',
        fmtstr = '%.1f',
        unit = 'C',
        warnlimits = (0,55),  # HW will switch off above 60 deg C
    ),
    '%s_waterflow' % setupname: device('nicos.devices.tango.Sensor',
        description = 'Cooling water flow',
        tangodevice = tango_base + 'plc/_water_flow',
        fmtstr = '%.1f',
        unit = 'l/s',
        warnlimits = (1.5,25),  # HW will switch off below 1 l/s, sensor saturates at 30 l/s
    ),
    '%s_heater' % setupname: device('nicos.devices.tango.NamedDigitalOutput',
        description = 'On/Off-State of the heater',
        tangodevice = tango_base + 'plc/_heater',
        mapping = {'on': 1, 'off': 0}
    ),
    '%s_pumpstate' % setupname: device('nicos.devices.tango.NamedDigitalInput',
        description = 'On/Off-State of the turbo pump',
        tangodevice = tango_base + 'plc/_state',
        mapping = {'on': 1, 'off': 0}
    ),
    '%s_vacuum' % setupname: device('nicos.devices.tango.Sensor',
        description = 'Vacuum in the oven',
        tangodevice = tango_base + 'plc/_vacuum',
        fmtstr = '%.1f',
        unit = 'mbar',
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s' % setupname: 100},
}

startupcode = '''
if T_%s.ramp == 0:
    printwarning('!!! The ramp rate of temperature controller is 0 !!!')
    printwarning('Please check the ramp rate of the temperature controller')
''' % (setupname,)
