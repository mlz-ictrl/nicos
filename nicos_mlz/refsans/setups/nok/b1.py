description = 'Slit B1 using Beckhoff controllers'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')
lprecision = 0.005
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

index_r = 0
index_s = 1

# just_ps     60.0    170.00  #um die Schrauben der PS zur freigabe der Justage zu erreichen oder zu fixieren
# transport   35.4    109.00  #zum einsetzen des Transportstiftes
# montage    -59.6     49.45  #zum Entfernen der beiden unteren Befestigungsschrauben
# 2021-03-16 14:42:47 +- 2.6mm

devices = dict(
    b1 = device(code_base + 'slits.DoubleSlit',
        description = 'b1 end of Chopperburg',
        fmtstr = 'zpos: %.3f, open: %.3f',
        slit_r = 'b1r',
        slit_s = 'b1s',
        unit = 'mm',
    ),
    b1r = device(code_base + 'slits.SingleSlit',
        # length: 13.5 mm
        description = 'b1 slit, reactor side',
        motor = 'b1r_motor',
        masks = {
            'slit': 2.75,  # 2021-03-18 14:28:39 TheoMH 0.0
            'point': 2.75,  # 2021-03-18 14:28:39 TheoMH 0.0
            'gisans': -117.25 * optic_values['gisans_scale'],  # -120.0
        },
        nok_start = 2374.0,
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        visibility = (),
    ),
    b1s = device(code_base + 'slits.SingleSlit',
        # length: 13.5 mm
        description = 'xxx slit, sample side',
        motor = 'b1s_motor',
        masks = {
            'slit': 2.65,  # 2021-03-18 14:28:39 TheoMH 0.0
            'point': 2.65,  # 2021-03-18 14:28:39 TheoMH 0.0
            'gisans': 2.65,  # 2021-03-18 14:28:39 TheoMH 0.0
        },
        nok_start = 2374.0,
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        visibility = (),
    ),
    b1r_motor = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M01), reactor side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_r*10,  # word adress
        slope = 10000,
        unit = 'mm',
        abslimits = (-133, 127),
        ruler = 233.155,
        visibility = (),
    ),
    b1s_motor = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M02), sample side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_s*10,  # word adress
        slope = 10000,
        unit = 'mm',
        abslimits = (-102, 170),
        ruler = 140.388,
        visibility = (),
    ),
)

alias_config = {
    'primary_aperture': {'b1.opening': 300},
}
