description = 'Slit H2 using Beckhoff controllers'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base'] + 'h2/plc/'
code_base = instrument_values['code_base']

devices = dict(
    h2_motor1 = device('nicos.devices.entangle.Actuator',
        description = 'Horizontal slit: KWS side. towards TOFTOF is plus',
        tangodevice = tango_base + 'axis1',
        unit = 'mm',
        visibility = (),
    ),
    h2_motor2 = device('nicos.devices.entangle.Actuator',
        description = 'Horizontal slit: TOFTOF side',
        tangodevice = tango_base + 'axis2',
        unit = 'mm',
        visibility = (),
    ),
    h2 = device('nicos.devices.generic.slit.HorizontalGap',
        description = 'Horizontal slit system',
        left = 'h2_motor1',
        right = 'h2_motor2',
        opmode = 'offcentered',
    ),
    h2_center = device('nicos.devices.generic.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.CenterGapAxis',
        alias = 'h2.center',
    ),
    h2_width = device('nicos.devices.generic.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.SizeGapAxis',
        alias = 'h2.width',
    ),
)
