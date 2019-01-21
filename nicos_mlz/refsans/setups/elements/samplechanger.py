description = 'Sample table devices'

group = 'optional'

tango_base = 'tango://refsanshw:10000/sample/phy_mo1/'

devices = dict(
    samplechanger = device('nicos.devices.generic.Axis',
        description = 'Samplechanger',
        motor = 'samplechanger_m',
        coder = 'samplechanger_e',
        precision = 0.01,
    ),
    samplechanger_m = device('nicos.devices.tango.Motor',
        description = 'Samplechanger axis motor',
        tangodevice = tango_base + 'samplechanger_m',
        lowlevel = True,
    ),
    samplechanger_e = device('nicos.devices.tango.Sensor',
        description = 'Samplechanger axis coder',
        tangodevice = tango_base + 'samplechanger_e',
        lowlevel = True,
    ),
)
