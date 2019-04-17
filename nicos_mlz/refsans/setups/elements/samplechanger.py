description = 'Sample table devices'

group = 'optional'

tango_base = 'tango://refsanshw:10000/sample/phy_mo1/'
coder_ss = 'm'


devices = dict(
    samplechanger = device('nicos.devices.generic.Axis',
        description = 'Samplechanger. towards TOFTOF is plus, motion limeted due to 45deg mounting',
        motor = 'samplechanger_m',
        coder = 'samplechanger_%s' % coder_ss,
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
