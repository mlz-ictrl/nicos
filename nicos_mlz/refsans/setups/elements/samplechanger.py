description = 'Sample table devices'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + 'sample/phy_mo1/'


devices = dict(
    samplechanger = device('nicos.devices.generic.Axis',
        description = 'Samplechanger. towards TOFTOF is plus',
        motor = 'samplechanger_m',
        coder = 'samplechanger_e',
        precision = 0.01,
    ),
    samplechanger_m = device('nicos.devices.tango.Motor',
        description = 'Samplechanger axis motor  100mm/3.5min',
        tangodevice = tango_base + 'samplechanger_m',
        lowlevel = True,
        abslimits = [14,350],
    ),
    samplechanger_e = device('nicos.devices.tango.Sensor',
        description = 'Samplechanger axis coder',
        tangodevice = tango_base + 'samplechanger_e',
        lowlevel = True,
    ),
)
