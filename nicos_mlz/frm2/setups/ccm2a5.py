description = 'High-Tc superconducting magnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'B_{setupname}': device('nicos.devices.entangle.RampActuator',
        description = 'magnetic field device',
        tangodevice = tango_base + 'plc/plc_magneticfield',
        unit = 'T',
        fmtstr = '%.3f',
        abslimits = (-2.5, 2.5),
        precision = 0.0005,
    ),
    f'B_{setupname}_readback': device('nicos.devices.entangle.AnalogInput',
        description = 'magnetic field device',
        tangodevice = tango_base + 'plc/plc_currentmonitor',
        unit = 'T',
        fmtstr = '%.3f',
        pollinterval = 1,
    ),
    f'{setupname}_current': device('nicos.devices.entangle.AnalogInput',
        description = 'Measured current through the leads',
        tangodevice = tango_base + 'plc/plc_transducer',
        unit = 'A',
        fmtstr = "%.1f",
        warnlimits = (-208, 208),
    ),
    f'{setupname}_watertemp': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of cooling water',
        tangodevice = tango_base + 'plc/plc_watertemp',
        unit = 'degC',
        fmtstr = "%.1f",
        warnlimits = (5, 45),
    ),
    f'{setupname}_waterflow': device('nicos.devices.entangle.AnalogInput',
        description = 'Flow rate of cooling water',
        tangodevice = tango_base + 'plc/waterflow',
        unit = 'l/min',
        fmtstr = "%.1f",
        warnlimits = (5, 10),
    ),
    f'{setupname}_compressor': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Compressor for cold head',
        tangodevice = tango_base + 'plc/plc_compressor',
        mapping = dict(on=1, off=0),
    ),
    f'{setupname}_T1': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of the first stage of the '
        'cryo-cooler',
        tangodevice = tango_base + 'hts_mss/t1',
        unit = 'K',
        warnlimits = (0, 44),
    ),
    f'{setupname}_T2': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of the second stage of the '
        'cryo-cooler',
        tangodevice = tango_base + 'hts_mss/t2',
        unit = 'K',
        warnlimits = (0, 14),
    ),
    f'{setupname}_TA': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of coil pack A',
        tangodevice = tango_base + 'hts_mss/t3',
        unit = 'K',
        warnlimits = (0, 19),
    ),
    f'{setupname}_TB': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of coil pack B',
        tangodevice = tango_base + 'hts_mss/t4',
        unit = 'K',
        warnlimits = (0, 19),
    ),
}

startupcode=f'''
B_{setupname}.ramp = 0.1
'''

alias_config = {
    'B': {f'B_{setupname}': 100},
}

extended = dict(
    representative = f'B_{setupname}',
)

monitor_blocks = dict(
    default = Block('2.5T Magnet (HTS)', [
        BlockRow(
             Field(name='Field', dev='B_ccm2a5', width=12),
        ),
        BlockRow(
            Field(name='Target', key='B_ccm2a5/target', width=12),
            Field(name='Readback', dev='B_ccm2a5_readback', width=12),
        ),
    ], setups=setupname),
    temperatures = Block('2.5T Magnet Temperature', [
        BlockRow(
             Field(name='T1', dev='ccm2a5_T1', width=12),
             Field(name='T2', dev='ccm2a5_T2', width=12),
        ),
        BlockRow(
             Field(name='TA', dev='ccm2a5_TA', width=12),
             Field(name='TB', dev='ccm2a5_TB', width=12),
        ),
    ], setups=setupname),
    plot = Block('2.5T Magnet plot', [
        BlockRow(
            Field(plot='30 min ccm2a5', name='30 min', dev='B_ccm2a5',
                  width=60, height=40, plotwindow=1800),
            Field(plot='30 min ccm2a5', name='Target', key='B_ccm2a5/target'),
            Field(plot='12 h ccm2a5', name='12 h', dev='B_ccm2a5', width=60,
                  height=40, plotwindow=12*3600),
            Field(plot='12 h ccm2a5', name='Target', key='B_ccm2a5/target'),
        ),
    ], setups=setupname),
)
