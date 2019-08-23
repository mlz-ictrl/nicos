description = 'Sample table devices'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + 'sample/phy_mo1/'


devices = dict(
    samplechanger = device('nicos.devices.generic.Axis',
        description = 'Samplechanger. towards TOFTOF is plus, motion limeted due to 45deg mounting',
        motor = 'samplechanger_m',
        coder = 'samplechanger_e',
        precision = 0.01,
    ),
    samplechanger_m = device('nicos.devices.tango.Motor',
        description = 'Samplechanger axis motor',
        tangodevice = tango_base + 'samplechanger_m',
        lowlevel = True,
        abslimits = [115,350],
    ),
    samplechanger_e = device('nicos.devices.tango.Sensor',
        description = 'Samplechanger axis coder',
        tangodevice = tango_base + 'samplechanger_e',
        lowlevel = True,
    ),
)
