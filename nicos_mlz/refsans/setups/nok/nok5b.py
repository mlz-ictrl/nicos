description = 'NOK5b using Beckhoff controllers'

group = 'lowlevel'



instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

index_r = 5
index_s = 6

devices = {
    '%s' % setupname : device(code_base + 'beckhoff.nok.DoubleMotorBeckhoffNOK',
        description = '%s layer optic' % setupname,
        tangodevice = tango_base + 'optic/io/modbus',
        ruler = [266.947, 300.101], #abs enc! 53.8985,
        nok_start = 4153.50,
        nok_end = 5872.70,
        nok_gap = 1.0,
        nok_motor = [4403.00, 5623.00],
        addresses = [0x3020+index_r*10, 0x3020+index_s*10],
        unit = 'mm, mm',
        fmtstr = '%.2f, %.2f',
        inclinationlimits = (-14.99, 14.99),
        masks = {
            'ng': optic_values['ng'],
            'rc': optic_values['ng'],
            'vc': optic_values['vc'],
            'fc': optic_values['fc'],
        },
    ),
}
