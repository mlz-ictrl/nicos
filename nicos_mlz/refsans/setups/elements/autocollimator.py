description = 'autocollimator, water subtracted, vendor Trioptic'

group = 'lowlevel'

all_lowlevel = False

instrument_values = configdata('instrument.values')

tango_host = instrument_values['tango_base'] + 'test/triangle/io'
code_base = instrument_values['code_base'] + 'triangle.'

devices = dict(
    autocollimator = device(code_base + 'TriangleMaster',
        description = description,
        tangodevice = tango_host,
        lowlevel = True,
        unit = '',
    ),
    autocollimator_theta = device(code_base + 'TriangleAngle',
        description = description + ', autocollimator Y on PC',
        lowlevel = all_lowlevel,
        index = 0,
        tangodevice = tango_host,
        scale = 1,
        unit = 'deg',
    ),
    autocollimator_phi = device(code_base + 'TriangleAngle',
        description = description + ', autocollimator X on PC',
        lowlevel = all_lowlevel,
        index = 1,
        tangodevice = tango_host,
        scale = -1,
        unit = 'deg',
    ),
)
