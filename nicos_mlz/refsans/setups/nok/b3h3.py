description = 'B3 aperture devices'

group = 'lowlevel'

lprecision = 0.01
instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    b3g = device('nicos.devices.generic.slit.HorizontalGap',
        description = 'slit system',
        left = 'b3s_motor',
        right = 'b3r_motor',
        opmode = 'offcentered',
    ),
    b3 = device(code_base + 'slits.DoubleSlitSequence',
        description = 'b3 and h3 inside Sample chamber. towards TOFTOF is plus',
        fmtstr = '%.3f, %.3f',
        adjustment = 'b3h3_frame',
        unit = 'mm',
        slit_r = 'b3r',
        slit_s = 'b3s',
        # nok_motor = [-1, -1],
    ),
    b3h3_frame = device('nicos.devices.generic.ManualSwitch',
        description = 'positioning Frame of b3h3',
        states = ['110mm', '70mm'],
    ),
    b3r = device(code_base + 'slits.SingleSlit',
       description = 'b3 slit, reactor side',
       visibility = (),
       motor = 'b3r_motor',
       nok_start = 11334.5,
       nok_end = 11334.5,
       masks = {
           'slit':  0.0,
           'point': 136.948400,
           'gisans': 136.948400,
       },
       unit = 'mm',
    ),
    b3s = device(code_base + 'slits.SingleSlit',
       description = 'b3 slit, sample side',
       visibility = (),
       motor = 'b3s_motor',
       nok_start = 11334.5,
       nok_end = 11334.5,
       masks = {
           'slit': 0.0,
           'point': 103.365400,
           'gisans': 103.365400,
       },
       unit = 'mm',
    ),
    b3r_motor = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'tbd',
        tangodevice = tango_base + 'refsans/b3/modbus',
        address = 0x3214+3*10, # decimal 12820
        slope = -10000,
        unit = 'mm',
        abslimits = (42 - 136.948400, 180.0 - 136.948400),
        ruler = -200.0 + 136.948400,
        visibility = (),
    ),
    b3s_motor = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'tbd',
        tangodevice = tango_base + 'refsans/b3/modbus',
        address = 0x3214+2*10, # decimal 12820
        slope = 10000,
        unit = 'mm',
        abslimits = (22.0 - 103.365400, 160.0 - 103.365400),
        ruler = 103.365400,
        visibility = (),
    ),
    h3g = device('nicos.devices.generic.slit.HorizontalGap',
        description = 'Horizontal slit system',
        left = 'h3s_motor',
        right = 'h3r_motor',
        opmode = 'offcentered',
    ),
    h3 = device(code_base + 'slits.DoubleSlit',
        description = 'h3 together with b3',
        fmtstr = 'zpos: %.3f, open: %.3f',
        maxheight = 80,
        unit = 'mm',
        slit_r = 'h3r',
        slit_s = 'h3s',
    ),
    h3r = device(code_base + 'slits.SingleSlit',
        description = 'h3 blade TOFTOF',
        motor = 'h3r_motor',
        masks = {
            'slit':   151.0, # 115.5,
            'point':  151.0,
            'gisans': 151.0,
        },
        visibility = (),
        unit = 'mm',
    ),
    h3s = device(code_base + 'slits.SingleSlit',
        description = 'h3 blade KWS',
        motor = 'h3s_motor',
        masks = {
            'slit':   48.0, # 83.5,
            'point':  48.0,
            'gisans': 48.0,
        },
        visibility = (),
        unit = 'mm',
    ),
    # h3r = device('nicos.devices.generic.Axis',
    #     description = 'h3, TOFTOF',
    #     motor = 'h3r_motor',
    #     # offset = 0.0,
    #     precision = 0.03,
    #     visibility = (),
    # ),
    # h3s = device('nicos.devices.generic.Axis',
    #     description = 'h3, ',
    #     motor = 'h3s_motor',
    #     # offset = 0.0,
    #     precision = 0.03,
    #     visibility = (),
    # ),
    h3r_motor = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'M1 from Reactor to Sample 1. Slit in Frame b3h3',
        tangodevice = tango_base + 'refsans/b3/modbus',
        address = 0x3214+0*10, # decimal 12820
        slope = -10000,
        unit = 'mm',
        # 2020-08-17 14:41:54 bslimits = (-193.0, 330.0),
        abslimits = (40.0, 180.0),
        ruler = -200.0,
        visibility = (),
    ),
    h3s_motor = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'M2 from Reactor to Sample 2. Slit in Frame b3h3',
        tangodevice = tango_base + 'refsans/b3/modbus',
        address = 0x3214+1*10, # decimal 12820
        slope = 10000,
        unit = 'mm',
        # 2020-08-17 14:28:44 abslimits = (-102.0, 170.0),
        abslimits = (20.5, 160.0),
        ruler = 0.0,
        visibility = (),
    ),
)

alias_config = {
    'last_aperture': {'b3.opening': 200},
}
