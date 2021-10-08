description = 'Sample table devices'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + 'sample/phy_mo1/'


devices = dict(
    samplechanger = device('nicos.devices.generic.Axis',
        description = 'Samplechanger. towards TOFTOF is plus',
        motor = 'samplechanger_motor',
        coder = 'samplechanger_enc',
        precision = 0.01,
    ),
    samplechanger_motor = device('nicos.devices.entangle.Motor',
        description = 'Samplechanger axis motor  100mm/3.5min 0,48mm/sec',
        tangodevice = tango_base + 'samplechanger_m',
        visibility = (),
        unit = 'mm',
        abslimits = [-186, 150], #MP offset==0 2021-03-29 13:18:30 abslimits = [14,350],
    ),
    samplechanger_enc = device('nicos.devices.entangle.Sensor',
        description = 'Samplechanger axis coder',
        tangodevice = tango_base + 'samplechanger_e',
        unit = 'mm',
        visibility = (),
    ),
)
