description = 'Slit H2 using Beckhoff controllers using PILS'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + 'h2/plc/'

devices = dict(
    h2_center = device('nicos.devices.tango.Actuator',
        description = 'Horizontal slit system: offset of the slit-center to the beam. towards TOFTOF is plus',
        tangodevice = tango_base + '_centeraxis',
        unit = 'mm',
        abslimits = (-69.5, 69.5),
    ),
    h2_width = device('nicos.devices.tango.Actuator',
        description = 'Horizontal slit system: opening of the slit',
        tangodevice = tango_base + '_widthaxis',
        unit = 'mm',
        abslimits = (0.05, 69.5),
    ),
)
