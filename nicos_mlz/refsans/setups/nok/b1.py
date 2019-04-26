description = 'Slit B1 using Beckhoff controllers'

group = 'lowlevel'

includes = ['aperture_primary']
instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
lprecision = 0.005
tango_base = 'tango://refsanshw.refsans.frm2.tum.de:10000/'

index_r = 0
index_s = 1

devices = dict(
    # b1_open = device('nicos_mlz.refsans.devices.slits.DoubleSlitOpen',
    #     description = 'Opening of b1 end of Chopperburg',
    #     fmtstr = '%.3f',
    #     classic = 'b1',
    #     unit = 'mm',
    # ),
    # b1_height = device('nicos_mlz.refsans.devices.slits.DoubleSlitHight',
    #     description = 'higth of b1 end of Chopperburg',
    #     fmtstr = '%.3f',
    #     classic = 'b1',
    #     unit = 'mm',
    # ),
    b1 = device('nicos_mlz.refsans.devices.slits.DoubleSlit',
        description = 'b1 end of Chopperburg',
        fmtstr = 'open: %.3f, zpos: %.3f',
        slit_r = 'b1r',
        slit_s = 'b1s',
        unit = 'mm',
    ),
    b1_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'b1 mode',
        device = 'b1',
        parameter = 'mode',
    ),
    b1r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'b1 slit, reactor side',
        motor = 'b1_r',
        masks = {
            'slit':   0.09,
            'point':  0.09,
            'gisans': 0.09,
        },
        nok_start = 2374.0,
        nok_length = 13.5,
        # nok_motor = [2380.0, 2387.5],
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        lowlevel = True,
    ),
    b1s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'xxx slit, sample side',
        motor = 'b1_s',
        masks = {
            'slit':   -0.09,
            'point':  -0.09,
            'gisans': -0.09,
        },
        nok_start = 2374.0,
        nok_length = 13.5,
        # nok_motor = [2380.0, 2387.5],
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        lowlevel = True,
    ),
    b1_r = device('nicos.devices.generic.Axis',
        description = 'B1, reactorside',
        motor = 'b1_rm',
        offset = 0.0,
        precision = lprecision,
        maxtries = 3,
        lowlevel = True,
    ),
    b1_s = device('nicos.devices.generic.Axis',
        description = 'B1, sampleside',
        motor = 'b1_sm',
        offset = 0.0,
        precision = lprecision,
        maxtries = 3,
        lowlevel = True,
    ),
    b1_rm = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M01), reactorside',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_r*10, # word adress
        slope = 10000,
        unit = 'mm',
        abslimits = (-133, 127), # XX: check values!
        ruler = 60.0,
        lowlevel = True,
    ),

    b1_rm_obs = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffPoti',
        description = 'Poti for B1 Reactor no ref',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_r*10, # word adress
        slope = 10000,
        abslimits = (-1000, 1000),
        poly = [-301.3,0.01626],
        lowlevel = True or showcase_values['hide_poti'],
    ),
    b1_rm_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'b1_rm',
         analog = 'b1_rm_obs',
         lowlevel = True or showcase_values['hide_acc'],
         unit = 'mm'
    ),
    b1_sm = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M02), sample side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_s*10, # word adress
        slope = 10000,
        unit = 'mm',
        abslimits = (-102, 170),
        ruler = -50.0,
        lowlevel = True,
    ),
    b1_sm_obs = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffPoti',
        description = 'Poti for B1 Sample no ref',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_s*10, # word adress
        slope = 10000,
        abslimits = (-1000, 1000),
        poly = [-249.17,0.01626],
        lowlevel = True or showcase_values['hide_poti'],
    ),
    b1_sm_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'b1_sm',
         analog = 'b1_sm_obs',
         lowlevel = True or showcase_values['hide_acc'],
         unit = 'mm'
    ),
)

alias_config = {
#    'primary_aperture': {'b1_open': 100},
}
