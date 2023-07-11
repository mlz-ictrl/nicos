description = 'High-Tc superconducting magnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'B_%s' % setupname: device('nicos.devices.entangle.RampActuator',
        description = 'magnetic field device',
        tangodevice = tango_base + 'plc/plc_magneticfield',
        unit = 'T',
        fmtstr = '%.3f',
        abslimits = (-2.5, 2.5),
        precision = 0.0005,
    ),
    'B_%s_readback' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'magnetic field device',
        tangodevice = tango_base + 'plc/plc_currentmonitor',
        unit = 'T',
        fmtstr = '%.3f',
        pollinterval = 1,
    ),
    '%s_current' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Measured current through the leads',
        tangodevice = tango_base + 'plc/plc_transducer',
        unit = 'A',
        fmtstr = "%.1f",
        warnlimits = (-208, 208),
    ),
    '%s_watertemp' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of cooling water',
        tangodevice = tango_base + 'plc/plc_watertemp',
        unit = 'degC',
        fmtstr = "%.1f",
        warnlimits = (5, 45),
    ),
    '%s_waterflow' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Flow rate of cooling water',
        tangodevice = tango_base + 'plc/waterflow',
        unit = 'l/min',
        fmtstr = "%.1f",
        warnlimits = (5, 10),
    ),
    '%s_compressor' % setupname: device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Compressor for cold head',
        tangodevice = tango_base + 'plc/plc_compressor',
        mapping = dict(on=1, off=0),
    ),
    '%s_T1' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of the first stage of the '
        'cryo-cooler',
        tangodevice = tango_base + 'hts_mss/t1',
        unit = 'K',
        warnlimits = (0, 44),
    ),
    '%s_T2' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of the second stage of the '
        'cryo-cooler',
        tangodevice = tango_base + 'hts_mss/t2',
        unit = 'K',
        warnlimits = (0, 14),
    ),
    '%s_TA' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of coil pack A',
        tangodevice = tango_base + 'hts_mss/t3',
        unit = 'K',
        warnlimits = (0, 19),
    ),
    '%s_TB' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of coil pack B',
        tangodevice = tango_base + 'hts_mss/t4',
        unit = 'K',
        warnlimits = (0, 19),
    ),
}

startupcode='''
B_%s.ramp = 0.1
''' % setupname

alias_config = {
    'B': {'B_%s' % setupname: 100},
}

extended = dict(
    representative = 'B_%s' % setupname,
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
