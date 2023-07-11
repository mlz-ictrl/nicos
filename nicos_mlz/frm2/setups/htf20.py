description = 'FRM II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'T_{setupname}': device('nicos.devices.entangle.TemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base + 'eurotherm/ctrl',
        abslimits = (0, 2000),
        precision = 0.2,
        fmtstr = '%.2f',
        unit = 'degC',
    ),
    f'{setupname}_watertemp': device('nicos.devices.entangle.Sensor',
        description = 'Cooling water temperature',
        tangodevice = tango_base + 'plc/_water_temp',
        fmtstr = '%.1f',
        unit = 'degC',
        warnlimits = (0,55),  # HW will switch off above 60 deg C
    ),
    f'{setupname}_waterflow': device('nicos.devices.entangle.Sensor',
        description = 'Cooling water flow',
        tangodevice = tango_base + 'plc/_water_flow',
        fmtstr = '%.2f',
        unit = 'l/s',
        warnlimits = (1.5/60.,30/60.),  # HW will switch off below 1 l/s, sensor saturates at 30 l/s
    ),
    f'{setupname}_heater': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'On/Off-State of the heater',
        tangodevice = tango_base + 'plc/_heater',
        mapping = {'on': 1, 'off': 0}
    ),
    f'{setupname}_state': device('nicos.devices.entangle.NamedDigitalInput',
        description = 'State of the rack',
        tangodevice = tango_base + 'plc/_state',
        mapping = {'unknown': 0}
    ),
    f'{setupname}_vacuum': device('nicos.devices.entangle.Sensor',
        description = 'Vacuum in the oven',
        tangodevice = tango_base + 'plc/_vacuum',
        fmtstr = '%.1e',
        unit = 'mbar',
    ),
    f'{setupname}_turbo': device('nicos.devices.entangle.NamedDigitalInput',
        description = 'State of the turbo pump',
        tangodevice = tango_base + 'plc/_turbo',
        mapping = {'on' : 1, 'off': 0}
    ),
    f'{setupname}_exgas_mode': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Exgas_mode',
        tangodevice = tango_base + 'plc/_exgas_mode',
        mapping = {'on': 1, 'off': 0}
    ),
    f'{setupname}_vac_valve': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'vaccum valve',
        tangodevice = tango_base + 'plc/_vac_valve',
        mapping = {'on': 1, 'off': 0}
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 100},
    'Ts': {f'T_{setupname}': 100},
}

extended = dict(
    representative = f'T_{setupname}',
)

startupcode = '''
if T_%s.ramp == 0:
    printwarning('!!! The ramp rate of temperature controller is 0 !!!')
    printwarning('Please check the ramp rate of the temperature controller')
''' % (setupname,)
