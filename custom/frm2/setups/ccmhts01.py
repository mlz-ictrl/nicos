description = 'High-Tc superconducting magnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'B_%s' % setupname  : device('devices.tango.AnalogOutput',
                         description = 'magnetic field device',
                         tangodevice = tango_base + 'plc/_magneticfield',
                         unit = 'T',
                         abslimits = (-2.2, 2.2),
                        ),
    'B_%s_readback' % setupname  : device('devices.tango.AnalogInput',
                         description = 'magnetic field device',
                         tangodevice = tango_base + 'plc/_currentmonitor',
                         unit = 'T',
                        ),
    '%s_current' % setupname  : device('devices.tango.AnalogInput',
                         description = 'magnet current',
                         tangodevice = tango_base + 'hts_mss/magnet_current',
                         unit = 'A',
                        ),
    '%s_voltage' % setupname  : device('devices.tango.AnalogInput',
                         description = 'magnet voltage',
                         tangodevice = tango_base + 'hts_mss/magnet_voltage',
                         unit = 'V',
                        ),
    '%s_watertemp' % setupname  : device('devices.tango.AnalogInput',
                         description = 'Temperature of cooling water',
                         tangodevice = tango_base + 'plc/_watertemp',
                         unit = 'degC',
                         warnlimits = (5, 25),
                        ),
    '%s_waterflow' % setupname  : device('devices.tango.AnalogInput',
                         description = 'Flow rate of cooling water',
                         tangodevice = tango_base + 'plc/_waterflow',
                         unit = 'l/s',
                         warnlimits = (0.5, 5),
                        ),
    '%s_compressor' % setupname  : device('devices.tango.NamedDigitalOutput',
                         description = 'Compressor for cold head',
                         tangodevice = tango_base + 'plc/_comp',
                         mapping = dict(on=1, off=0),
                        ),
    '%s_T1' % setupname  : device('devices.tango.AnalogInput',
                         description = 'Temperature of the first stage of the '
                            'cryo-cooler',
                         tangodevice = tango_base + 'hts_mss/t1',
                         unit = 'K',
                         warnlimits = (0, 44),
                        ),
    '%s_T2' % setupname  : device('devices.tango.AnalogInput',
                         description = 'Temperature of the second stage of the '
                            'cryo-cooler',
                         tangodevice = tango_base + 'hts_mss/t2',
                         unit = 'K',
                         warnlimits = (0, 12),
                        ),
    '%s_TA' % setupname  : device('devices.tango.AnalogInput',
                         description = 'Temperature of coil pack A',
                         tangodevice = tango_base + 'hts_mss/t3',
                         unit = 'K',
                         warnlimits = (0, 20),
                        ),
    '%s_TB' % setupname  : device('devices.tango.AnalogInput',
                         description = 'Temperature of coil pack B',
                         tangodevice = tango_base + 'hts_mss/t4',
                         unit = 'K',
                         warnlimits = (0, 20),
                        ),
}

alias_config = {
    'B': {'B_%s' % setupname: 100},
}
