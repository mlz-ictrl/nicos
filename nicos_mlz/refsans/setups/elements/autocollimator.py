description = 'autocollimator, water subtracted, vendor Trioptic'

group = 'lowlevel'

all_lowlevel = {'metadata', 'devlist', 'namespace'}

instrument_values = configdata('instrument.values')

tango_host = instrument_values['tango_base'] + 'test/triangle/io'
code_base = instrument_values['code_base'] + 'triangle.'

devices = dict(
    autocollimator = device(code_base + 'TriangleMaster',
        description = description,
        tangodevice = tango_host,
        visibility = (),
        unit = '',
    ),
    autocollimator_theta = device(code_base + 'TriangleAngle',
        description = description + ', autocollimator Y on PC',
        visibility = all_lowlevel,
        index = 0,
        tangodevice = tango_host,
        scale = 1,
        unit = 'deg',
    ),
    autocollimator_phi = device(code_base + 'TriangleAngle',
        description = description + ', autocollimator X on PC',
        visibility = all_lowlevel,
        index = 1,
        tangodevice = tango_host,
        scale = -1,
        unit = 'deg',
    ),
)
