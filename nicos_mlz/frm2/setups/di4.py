
description = 'Triton dilution refrigerator'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

_heater_ranges = {'0: Off': 0,
                 '1: 31.6 µA': 1,
                 '2: 100 µA': 2,
                 '3: 316 µA': 3,
                 '4: 1.00 mA': 4,
                 '5: 3.16 mA': 5,
                 '6: 10.0 mA': 6,
                 '7: 31.6 mA': 7,
                 '8: 100 mA': 8,}

devices = {
    f'T_{setupname}':
        device('nicos.devices.entangle.TemperatureController',
               description = 'Temperature controller',
               tangodevice = tango_base + 'lakeshore/temp_control',
               fmtstr = '%.3f', pollinterval = 10,),
    f'T_{setupname}_heater_range':
        device('nicos.devices.entangle.NamedDigitalOutput',
               description = 'Heater range',
               tangodevice = tango_base + 'lakeshore/tc_heaterrange',
               mapping = _heater_ranges,
               fmtstr = '%.0f', pollinterval = 10,),
    f'{setupname}_still_heater':
        device('nicos.devices.entangle.AnalogOutput',
               description = 'Still heater power fraction',
               tangodevice = tango_base + 'lakeshore/tc_still',
               fmtstr = '%.0f', pollinterval = 10,),
    f'{setupname}_warm_up_heater':
        device('nicos.devices.entangle.AnalogOutput',
               description = 'Warm-up heater power fraction',
               tangodevice = tango_base + 'lakeshore/tc_warm-up',
               fmtstr = '%.0f', pollinterval = 10,),
    f'T_{setupname}_sorb':
        device('nicos.devices.entangle.Sensor',
               description = 'Inner vacuum can sorbent, temperature (ch 1)',
               tangodevice = tango_base + f'lakeshore/sensor1',
               fmtstr = '%.3f', pollinterval = 10, unit = 'K'),
    f'{setupname}_R_sorb':
        device('nicos.devices.entangle.Sensor',
               description = 'Inner vacuum can sorbent, sensor resistance',
               tangodevice = tango_base + f'lakeshore/sensor1R',
               fmtstr = '%.3f', pollinterval = 10, unit = 'Ohm',
               visibility = (),),
    f'T_{setupname}_exch':
        device('nicos.devices.entangle.Sensor',
               description = 'Heat exchanger, temperature (ch 2)',
               tangodevice = tango_base + f'lakeshore/sensor2',
               fmtstr = '%.3f', pollinterval = 10, unit = 'K'),
    f'{setupname}_R_exch':
        device('nicos.devices.entangle.Sensor',
               description = 'Heat exchanger, sensor resistance',
               tangodevice = tango_base + f'lakeshore/sensor2R',
               fmtstr = '%.3f', pollinterval = 10, unit = 'Ohm',
               visibility = (),),
    f'T_{setupname}_JT':
        device('nicos.devices.entangle.Sensor',
               description = 'Joule-Thomson stage, temperature (ch 3)',
               tangodevice = tango_base + f'lakeshore/sensor3',
               fmtstr = '%.3f', pollinterval = 10, unit = 'K'),
    f'{setupname}_R_JT':
        device('nicos.devices.entangle.Sensor',
               description = 'Joule-Thomson stage, sensor resistance',
               tangodevice = tango_base + f'lakeshore/sensor3R',
               fmtstr = '%.3f', pollinterval = 10, unit = 'Ohm',
               visibility = (),),
    f'T_{setupname}_still':
        device('nicos.devices.entangle.Sensor',
               description = 'Still, temperature (ch 4)',
               tangodevice = tango_base + f'lakeshore/sensor4',
               fmtstr = '%.3f', pollinterval = 10, unit = 'K'),
    f'{setupname}_R_still':
        device('nicos.devices.entangle.Sensor',
               description = 'Still, sensor resistance',
               tangodevice = tango_base + f'lakeshore/sensor4R',
               fmtstr = '%.3f', pollinterval = 10, unit = 'Ohm',
               visibility = (),),
    f'T_{setupname}_mc':
        device('nicos.devices.entangle.Sensor',
               description = ' Mixing chamber, temperature (ch 5)',
               tangodevice = tango_base + f'lakeshore/sensor5',
               fmtstr = '%.3f', pollinterval = 10, unit = 'K'),
    f'{setupname}_R_mc':
        device('nicos.devices.entangle.Sensor',
               description = 'Mixing chamber, sensor resistance',
               tangodevice = tango_base + f'lakeshore/sensor5R',
               fmtstr = '%.3f', pollinterval = 10, unit = 'Ohm',
               visibility = (),),
}

pressure_sensors = {
    1: 'Tank pressure',
    2: 'Condense pressure',
    3: 'Still pressure',
    5: 'Compressor pressure',}

for i in [1, 2, 3, 5]:
    devices[f'{setupname}_p{i}'] = \
        device('nicos.devices.entangle.Sensor',
               description = pressure_sensors[i],
               tangodevice = tango_base + f'triton/p{i}',
               fmtstr = '%.3g', pollinterval = 1,)

alias_config = {
    'T':  {f'T_{setupname}': 300,},
    'Ts': {f'T_{setupname}_mc': 300,},
}
