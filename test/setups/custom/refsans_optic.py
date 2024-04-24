description = 'NOK Devices for REFSANS, main file including all'

group = 'lowlevel'

gisans_scale = 1
ng = 0.0
rc = 22.5
vc = 37.5
fc = 50.0

devices = dict(
    b1 = device('nicos.devices.generic.slit.VerticalGap',
        opmode = 'offcentered',
        min_opening = -1,
        top = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (-133, 127),
                unit = 'mm',
            ),
            masks = {
                'slit': 2.75,
                'point': 2.75,
                'gisans': -117.25 * gisans_scale,
            },
            nok_start = 2374.0,
            nok_end = 2387.5,
            nok_gap = 0,
            unit = 'mm',
        ),
        bottom = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (-102, 170),
                unit = 'mm',
            ),
            masks = {
                'slit': 2.65,
                'point': 2.65,
                'gisans': 2.65,
            },
            nok_start = 2374.0,
            nok_end = 2387.5,
            nok_gap = 0,
            unit = 'mm',
        ),
    ),
    b2 = device('nicos.devices.generic.slit.VerticalGap',
        opmode = 'offcentered',
        min_opening = -1,
        top = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (-288, 227),
                unit = 'mm',
            ),
            nok_start = 11049.50,
            nok_end = 11064.50,
            nok_gap = 1.0,
            masks = {
                'slit': -5.775,
                'point': -5.775,
                'gisans': -5.775,
            },
            unit = 'mm',
        ),
        bottom = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (-291, 224),
                unit = 'mm',
            ),
            nok_start = 11049.50,
            nok_end = 11064.50,
            nok_gap = 1.0,
            masks = {
                'slit': 4.775,
                'point': -4.775,
                'gisans': -79 * gisans_scale,
            },
            unit = 'mm',
        ),
    ),
    b3 = device('nicos_mlz.refsans.devices.slits.DoubleSlitSequence',
        fmtstr = '%.3f, %.3f',
        adjustment = device('nicos.devices.generic.ManualSwitch',
            states = ['110mm', '70mm'],
        ),
        unit = 'mm',
        slit_r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (42 - 136.948400, 180.0 - 136.948400),
                unit = 'mm',
            ),
            nok_start = 11334.5,
            nok_end = 11334.5,
            masks = {
                'slit':  0.0,
                'point': 136.948400,
                'gisans': 136.948400,
            },
            unit = 'mm',
        ),
        slit_s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (22.0 - 103.365400, 160.0 - 103.365400),
                unit = 'mm',
            ),
            nok_start = 11334.5,
            nok_end = 11334.5,
            masks = {
                'slit': 0.0,
                'point': 103.365400,
                'gisans': 103.365400,
            },
            unit = 'mm',
        ),
    ),
    bs1 = device('nicos.devices.generic.slit.VerticalGap',
        opmode = 'offcentered',
        top = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (-173.0, 17.0),
                unit = 'mm',
            ),
            nok_start = 9764.5,
            nok_end = 9770.5,
            nok_gap = 18.0,
            masks = {
                'slit': -1.10,
                'point': 0.70,
                'gisans': -40.915 * gisans_scale,
            },
            unit = 'mm',
        ),
        bottom = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (-183.002, 135.5),
                unit = 'mm',
            ),
            nok_start = 9764.5,
            nok_end = 9770.5,
            nok_gap = 18.0,
            masks = {
                'slit': -1.00,
                'point': -1.00,
                'gisans':-2.255,
            },
            unit = 'mm',
        ),
    ),
    zb0 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-155.7889, 28.1111),
            unit = 'mm',
        ),
        nok_start = 4121.5,
        nok_end = 4134.5,
        nok_gap = 1,
        masks = {
            'slit': 0,
            'point': 0,
            'gisans': -110 * gisans_scale,
        },
        unit = 'mm',
    ),
    zb1 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-178.9,  53.9),
            unit = 'mm',
        ),
        offset = 0.0,
        nok_start = 5873.6,
        nok_end = 5886.6,
        masks = {
            'slit':    0,
            'point':   0,
            'gisans':  -110 * gisans_scale,
        },
        unit = 'mm',
    ),
    zb2 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-215.69, 93.0),
            unit = 'mm',
        ),
        nok_start = 7633.5,
        nok_end = 7639.5,
        nok_gap = 1.0,
        offset = 0.0,
        masks = {
            'slit':   -2,
            'point':  -2,
            'gisans': -122.0 * gisans_scale,
        },
        unit = 'mm',
    ),
    zb3 = device('nicos.devices.generic.slit.VerticalGap',
        opmode = 'offcentered',
        top = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (-216.0, 101.0),
                unit = 'mm',
            ),
            nok_start = 8856.5,
            nok_end = 8869.5,
            nok_gap = 1.0,
            masks = {
                'slit': -1.8,
                'point': -1.8,
                'gisans': -110.15 * gisans_scale,
            },
            unit = 'mm',
        ),
        bottom = device('nicos_mlz.refsans.devices.slits.SingleSlit',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (-112.0, 108.5),
                unit = 'mm',
            ),
            nok_start = 8856.5,
            nok_end = 8869.5,
            nok_gap = 1.0,
            masks = {
                'slit': 0.3,
                'point': 0.3,
                'gisans': 0.3,
            },
            unit = 'mm',
        ),
    ),
    sc2 = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-150, 130),
        unit = 'mm',
    ),
    disc3 = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-43, 48),
        unit = 'mm',
    ),
    disc4 = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-30, 46),
        unit = 'mm',
    ),
    nok2 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        fmtstr = '%.2f, %.2f',
        nok_start = 334.0,
        nok_end = 634.0,
        nok_gap = 1.0,
        inclinationlimits = (-11.34, 13.61),
        motor_r = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-22.36, 10.88),
            unit = 'mm',
        ),
        motor_s = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-21.61, 6.885),
            unit = 'mm',
        ),
        nok_motor = [408.5, 585.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': ng,
            'rc': ng,
            'vc': ng,
            'fc': ng,
        },
    ),
    nok3 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        fmtstr = '%.2f, %.2f',
        nok_start = 680.0,
        nok_end = 1280.0,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-21.967, 47.783),
            unit = 'mm',
        ),
        motor_s = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-20.9435, 40.8065),
            unit = 'mm',
        ),
        nok_motor = [831.0, 1131.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': ng,
            'rc': rc,
            'vc': ng,
            'fc': ng,
        },
    ),
    nok4 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        fmtstr = '%.2f, %.2f',
        nok_start = 1326.0,
        nok_end = 2326.0,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-20.477, 48.523),
            unit = 'mm',
        ),
        motor_s = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-21.3025, 41.1975),
            unit = 'mm',
        ),
        nok_motor = [1477.0, 2177.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': ng,
            'rc': rc,
            'vc': ng,
            'fc': ng,
        },
    ),
    nok5a = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        # length: 1719.20 mm
        description = 'NOK5a',
        fmtstr = '%.2f, %.2f',
        nok_start = 2418.50,
        nok_end = 4137.70,
        nok_gap = 1.0,
        nok_motor = [3108.00, 3888.00],
        offsets = (0.0, 0.0),
        inclinationlimits = (-100, 100),
        motor_r = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-70.0,67.68),
        ),
        motor_s = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-79.0,77.85),
        ),
        backlash = -2,
        masks = {
            'ng': ng,
            'rc': ng,
            'vc': vc,
            'fc': fc,
            # 'pola': pola,
        },
        mode = 'ng',
    ),
    nok5b = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        fmtstr = '%.2f, %.2f',
        nok_start = 4153.50,
        nok_end = 5872.70,
        nok_gap = 1.0,
        offsets = (0.0, 0.0),
        inclinationlimits = (-100, 100),
        motor_r = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-37.9997, 91.9003),
        ),
        motor_s = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-53.7985, 76.1015),
        ),
        nok_motor = [4403.00, 5623.00],
        backlash = -2,
        masks = {
            'ng': 1.4 + ng,
            'rc': 1.4 + ng,
            'vc': 1.4 + vc,
            'fc': 1.4 + fc,
        },
        mode = 'ng',
    ),
    nok6 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        fmtstr = '%.2f, %.2f',
        nok_start = 5887.5,
        nok_end = 7607.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-66.2, 96.59125),
            unit = 'mm',
        ),
        motor_s = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-81.0, 110.875),
            unit = 'mm',
        ),
        nok_motor = [6137.0, 7357.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': ng,
            'rc': ng,
            'vc': vc,
            'fc': fc,
        },
        mode = 'ng',
    ),
    nok7 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        fmtstr = '%.2f, %.2f',
        nok_start = 7665.5,
        nok_end = 8855.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-89.475, 116.1),
            unit = 'mm',
        ),
        motor_s = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-96.94, 125.56),
            unit = 'mm',
        ),
        nok_motor = [7915.0, 8605.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': ng,
            'rc': ng,
            'vc': vc,
            'fc': fc,
        },
        mode = 'ng',
    ),
    nok8 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        fmtstr = '%.2f, %.2f',
        nok_start = 8870.5,
        nok_end = 9750.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-102.835, 128.415),
            unit = 'mm',
        ),
        motor_s = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-104.6, 131.65),
            unit = 'mm',
        ),
        nok_motor = [9120.0, 9500.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': ng,
            'rc': ng,
            'vc': vc,
            'fc': fc,
        },
        mode = 'ng',
    ),
    nok9 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        nok_start = 9773.5,
        fmtstr = '%.2f, %.2f',
        nok_end = 10613.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-112.03425, 142.95925),
            unit = 'mm',
        ),
        motor_s = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-114.51425, 142.62775),
            unit = 'mm',
        ),
        nok_motor = [10023.5, 10362.7],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': ng,
            'rc': ng,
            'vc': vc,
            'fc': fc,
        },
        mode = 'ng',
    ),
    optic = device('nicos_mlz.refsans.devices.optic.Optic',
        description = 'Beam optic',
        b1 = 'b1',
        b2 = 'b2',
        b3 = 'b3',
        bs1 = 'bs1',
        nok2 = 'nok2',
        nok3 = 'nok3',
        nok4 = 'nok4',
        nok5a = 'nok5a',
        nok5b = 'nok5b',
        nok6 = 'nok6',
        nok7 = 'nok7',
        nok8 = 'nok8',
        nok9 = 'nok9',
        sc2 = 'sc2',
        zb0 = 'zb0',
        zb1 = 'zb1',
        zb2 = 'zb2',
        zb3 = 'zb3',
    setting ={
        'horizontal'          :{
            'nok2'  : [   0.0,        0.0],             #01
            'nok3'  : [   0.0,        0.0],             #02
            'nok4'  : [   0.0,        0.0],             #03
            'b1'    : [   0.0,       -1.0],             #04
            'nok5a' : [   0.0,        0.0],             #05
            'zb0'   :     0.0,                          #06
            'nok5b' : [   0.0,        0.0],             #07
            'zb1'   :     0.0,                          #08
            'nok6'  : [   0.0,        0.0],             #09
            'zb2'   :     0.0,                          #10
            'nok7'  : [   0.0,        0.0],             #11
            'zb3'   : [   0.0,       12.0],             #12
            'nok8'  : [   0.0,        0.0],             #13
            'bs1'   : [   0.0,       12.0],             #14
            'nok9'  : [   0.0,        0.0],             #15
            'sc2'   :     0.0,                          #16
            'b2'    : [   0.0,       -1.0],             #17
            'b3'    : [   0.0,        0.0],             #18
            },
        '12mrad_b3_789'   :{
            #'disk4' : 0.0,                          #
            #'disk3' : 0.0,                          #
            'nok2'  : [   0.0,        0.0],             #01
            'nok3'  : [   0.0,        0.0],             #02
            'nok4'  : [   0.0,        0.0],             #03
            'b1'    : [   0.0,       -1.0],             #04
            'nok5a' : [   0.0,        0.0],             #05
            'zb0'   :     0.0,                          #06
            'nok5b' : [   0.0,        0.0],             #07
            'zb1'   :     0.0,                          #08
            'nok6'  : [   0.0,        0.0],             #09
            'zb2'   :     0.0,                          #10
            'nok7'  : [  -1.244343,  -5.384393],        #11
            'zb3'   : [  -1.6728803, 12.08400403],      #12
            'nok8'  : [  -8.474430, -10.754457],        #13
            'bs1'   : [ -12.719411,  12.066003],        #14
            'nok9'  : [ -15.791558,- 19.862153],        #15
            'sc2'   :   -23.369922,                     #16
            'b2'    : [ -28.194153, - 0.819991],        #17
            'b3'    : [ -31.464310,   0.120006],        #18
            },
        '12mrad_b3_12.000'    :{
            #'disk4' : -12.468598498473538,                          #
            #'disk3' : -12.048578337312254,                          #
            'nok2'  : [  -0.470934,  -1.529946],        #01
            'nok3'  : [  -3.005964,  -4.805986],        #02
            'nok4'  : [  -6.882011, -11.082061],        #03
            'b1'    : [ -12.645607,  -1.0   ],          #04 12.090004320248847
            'nok5a' : [ -21.517249, -30.517249],        #05
            'zb0'   :   -33.583612             ,        #06
            'nok5b' : [ -36.877770, -51.518473],        #07
            'zb1'   :   -54.392610             ,        #08
            'nok6'  : [ -57.686769, -72.327472],        #09
            'zb2'   :   -75.213610             ,        #10
            'nok7'  : [ -79.023793, -87.304190],        #11
            'zb3'   : [ -90.208330,  12.084004],        #12
            'nok8'  : [ -93.484487, -98.044706],        #13
            'bs1'   : [-101.254860,  12.066003],        #14
            'nok9'  : [-104.327008,-108.397603],        #15
            'sc2'   :  -111.905371,                     #16
            'b2'    : [-116.729603,  -1.0],             #17 12.180008640497693
            'b3'    : [ -60.2,        0.0       ],      #18
            },

        '12mrad_b3_13.268'    :{
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [  -1.541887,  -3.532116],        #02
            'nok4'  : [  -5.827513, -10.471382],        #03
            'b1'    : [ -11.686477,  -1.0  ],           #04   12.099516
            'nok5a' : [ -22.571213, -30.371213],        #05
            # Due to inclimit, org is 2021-05-19
            # 'nok5a' : [ -21.971213, -30.971213],      #05
            'zb0'   :   -34.837178             ,        #06
            # Due to a mechanical limit the values are reduced by 1
            # normally the values should be:
            # 'nok5b' : [ -38.479458, -54.667368],      #07
            'nok5b' : [ -38.079458, -53.067368],        #07
            # Due to a mechanical limit the values are reduced by 1
            # normally the values should be:
            # 'nok5b' : [ -37.479458, -53.667368],      #07
            'zb1'   :   -57.845240             ,        #08
            'nok6'  : [ -61.487520, -77.675430],        #09
            'zb2'   :   -80.866571             ,        #10
            'nok7'  : [ -85.079409, -94.234866],        #11
            'zb3'   : [ -97.445910,  12.092881],        #12
            'nok8'  : [-100.068287,-105.110423],        #13
            # Due to a mechanical limit the values are reduced by 1
            # normally the values should be:
            #'nok8'  : [-101.068287,-106.110423],       #13
            'bs1'   : [-109.659821,  12.072978],        #14
            # Due to a mechanical limit the values are reduced by 1.5
            # normally the values should be:
            # 'nok9'  : [-113.056628,-117.557398],      #15
            'nok9'  : [-111.556628,-115.057398],        #15
            'sc2'   :  -121.435862             ,        #16
            'b2'    : [-126.769911,  -1.0],             #17   12.199032
            'b3'    : [  0.0,         0.0],             #18
            },
        '12mrad_b2_12.254_eng'    :{
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [  -1.882604,  -3.720727],        #02
            'nok4'  : [  -5.840696, -10.129650],        #03
            'b1'    : [ -10.793251,  -1.0     ],        #04   12.091910
            'nok5a' : [ -19.947954, -28.947954],        #05
            'zb0'   :   -32.174487             ,        #06
            'nok5b' : [ -35.538379, -50.489007],        #07
            'zb1'   :   -53.423987             ,        #08
            'nok6'  : [ -56.787878, -71.738507],        #09
            'zb2'   :   -74.685741             ,        #10
            'nok7'  : [ -78.576581, -87.032264],        #11
            'zb3'   : [ -89.997881,  12.085782],        #12
            'nok8'  : [ -93.343390, -98.000143],        #13
            'bs1'   : [-101.278252,  12.067400],        #14
            'nok9'  : [-104.415433,-108.572198],        #15
            'sc2'   :  -112.154222             ,        #16
            'b2'    : [-117.080576,  -1.0   ],          #17   12.183819
            'b3'    : [   0.0,        0.0],             #18
            },
        '12mrad_b2_12.88_big'    :{
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [  -1.672260,  -3.604287],        #02
            'nok4'  : [  -5.832558, -10.340620],        #03
            'b1'    : [ -11.344687,  -1.0],             #04   12.096605
            'nok5a' : [ -21.197021, -30.197021],        #05
            'zb0'   :   -33.818310             ,        #06
            'nok5b' : [ -37.354066, -53.068535],        #07
            'zb1'   :   -56.153465             ,        #08
            'nok6'  : [ -59.689221, -75.403690],        #09
            'zb2'   :   -78.501501             ,        #10
            'nok7'  : [ -82.591127, -91.478819],        #11
            'zb3'   : [ -94.595951,  12.090165],        #12
            'nok8'  : [ -98.112385,-103.007056],        #13
            'bs1'   : [-106.452647,  12.070844],        #14
            'nok9'  : [-109.750109,-114.119247],        #15
            'sc2'   :  -117.884279             ,        #16
            'b2'    : [-123.062325,  -1.0],             #17   12.193211
            'b3'    : [   0.0,        0.0],             #18
            },
        '48mrad'              :{
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [   0.000000,   0.000000],        #02
            'nok4'  : [   0.000000,   0.000000],        #03
            'b1'    : [   0.000000,  -1.000000],        #04   12.0
            'nok5a' : [   0.000000,   0.000000],        #05
            'zb0'   :     0.000000             ,        #06
            'nok5b' : [   0.000000,   0.000000],        #07
            'zb1'   :     0.000000             ,        #08
            'nok6'  : [   0.000000,   0.000000],        #09
            'zb2'   :     0.000000             ,        #10
            'nok7'  : [  -1.858601, -10.138999],        #11
            'zb3'   : [ -14.088305,  12.168032],        #12
            'nok8'  : [ -24.358282, -38.044194],        #13
            'bs1'   : [ -47.176917 , 12.264203],        #14
            'nok9'  : [ -59.474363, -75.768478],        #15
            'sc2'   :   -89.809664             ,        #16
            'b2'    : [-109.120497,  -1.0],             #17   12.720553
            'b3'    : [ -62.2,        0.0],             #18
            },

        '54mrad'              :{
            # 'disk4' : 0.0,
            # 'disk3' : 0.0,
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [   0.000000,   0.000000],        #02
            'nok4'  : [   0.000000,   0.000000],        #03
            'b1'    : [   0.000000,  -1.000000],        #04   12.0
            'nok5a' : [   0.000000,   0.000000],        #05
            'zb0'   :     0.000000             ,        #06
            'nok5b' : [   0.000000,   0.000000],        #07
            'zb1'   :     0.000000             ,        #08
            'nok6'  : [   0.000000,   0.000000],        #09
            'zb2'   :     0.000000             ,        #10
            'nok7'  : [  -1.34086695,-10.656433],       #11
            'zb3'   : [ -15.850152,   12.189046],       #12
            'nok8'  : [ -26.6536288, -42.052049],       #13
            'bs1'   : [ -53.080527 ,  12.29728902],     #14
            'nok9'  : [ -66.917980,  -85.252604],       #15
            'sc2'   :  -101.0521646             ,       #16
            'b2'    : [-122.781289,   -1.0     ],       #17   12.810788239415222
            'b3'    : [ -77.2,         0.0     ],       #18   12.540525492943482
            },

        },
        masks = {
            '12mrad234'           :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'fc','zb0':  'slit','nok5b':'fc','zb1':  'slit','nok6':'fc','zb2':  'slit','nok7':'fc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            '12mrad789'           :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'fc','zb0':  'slit','nok5b':'fc','zb1':  'slit','nok6':'fc','zb2':  'slit','nok7':'ng','zb3':  'slit','nok8':'ng','bs1':  'slit','nok9':'ng','b2':  'slit','b3':'slit'},
            '48mrad'              :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'vc','zb0':  'slit','nok5b':'vc','zb1':  'slit','nok6':'vc','zb2':  'slit','nok7':'ng','zb3':  'slit','nok8':'ng','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'fc:nok5a'            :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'fc','zb0':  'slit','nok5b':'fc','zb1':  'slit','nok6':'fc','zb2':  'slit','nok7':'fc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'fc:nok5b'            :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'ng','zb0':  'slit','nok5b':'fc','zb1':  'slit','nok6':'fc','zb2':  'slit','nok7':'fc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'fc:nok6'             :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'ng','zb0':  'slit','nok5b':'ng','zb1':  'slit','nok6':'fc','zb2':  'slit','nok7':'fc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'fc:nok7'             :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'ng','zb0':  'slit','nok5b':'ng','zb1':  'slit','nok6':'ng','zb2':  'slit','nok7':'fc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'fc:nok8'             :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'ng','zb0':  'slit','nok5b':'ng','zb1':  'slit','nok6':'ng','zb2':  'slit','nok7':'ng','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'fc:nok9'             :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'ng','zb0':  'slit','nok5b':'ng','zb1':  'slit','nok6':'ng','zb2':  'slit','nok7':'ng','zb3':  'slit','nok8':'ng','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'gisans'              :{'nok2':'ng','nok3':'ng','nok4':'rc','b1':'gisans','nok5a':'fc','zb0':'gisans','nok5b':'fc','zb1':'gisans','nok6':'fc','zb2':'gisans','nok7':'fc','zb3':'gisans','nok8':'fc','bs1':'gisans','nok9':'fc','b2':'gisans','b3':'slit'},
            'gisans789'           :{'nok2':'ng','nok3':'ng','nok4':'rc','b1':'gisans','nok5a':'fc','zb0':'gisans','nok5b':'fc','zb1':'gisans','nok6':'fc','zb2':'gisans','nok7':'ng','zb3':'gisans','nok8':'ng','bs1':'gisans','nok9':'fc','b2':'gisans','b3':'slit'},
            'neutronguide'        :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'ng','zb0':  'slit','nok5b':'ng','zb1':  'slit','nok6':'ng','zb2':  'slit','nok7':'ng','zb3':  'slit','nok8':'ng','bs1':  'slit','nok9':'ng','b2':  'slit','b3':'slit'},
            'point'               :{'nok2':'ng','nok3':'rc','nok4':'ng','b1':  'slit','nok5a':'fc','zb0':  'slit','nok5b':'fc','zb1':  'slit','nok6':'fc','zb2':  'slit','nok7':'fc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'vc:nok5a'            :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'vc','zb0':  'slit','nok5b':'vc','zb1':  'slit','nok6':'vc','zb2':  'slit','nok7':'vc','zb3':  'slit','nok8':'vc','bs1':  'slit','nok9':'vc','b2':  'slit','b3':'slit'},
            'vc:nok5a_fc:nok5b'   :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'vc','zb0':  'slit','nok5b':'fc','zb1':  'slit','nok6':'fc','zb2':  'slit','nok7':'fc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'vc:nok5a_fc:nok6'    :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'vc','zb0':  'slit','nok5b':'vc','zb1':  'slit','nok6':'fc','zb2':  'slit','nok7':'fc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'vc:nok5a_fc:nok7'    :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'vc','zb0':  'slit','nok5b':'vc','zb1':  'slit','nok6':'vc','zb2':  'slit','nok7':'fc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'vc:nok5a_fc:nok8'    :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'vc','zb0':  'slit','nok5b':'vc','zb1':  'slit','nok6':'vc','zb2':  'slit','nok7':'vc','zb3':  'slit','nok8':'fc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'vc:nok5a_fc:nok9'    :{'nok2':'ng','nok3':'ng','nok4':'ng','b1':  'slit','nok5a':'vc','zb0':  'slit','nok5b':'vc','zb1':  'slit','nok6':'vc','zb2':  'slit','nok7':'vc','zb3':  'slit','nok8':'vc','bs1':  'slit','nok9':'fc','b2':  'slit','b3':'slit'},
            'vc:nok5b'            :{},
            'vc:nok5b_fc:nok6'    :{},
            'vc:nok5b_fc:nok7'    :{},
            'vc:nok5b_fc:nok8'    :{},
            'vc:nok5b_fc:nok9'    :{},
            'vc:nok6'             :{},
            'vc:nok6_fc:nok7'     :{},
            'vc:nok6_fc:nok8'     :{},
            'vc:nok6_fc:nok9'     :{},
            'vc:nok7'             :{},
            'vc:nok7_fc:nok8'     :{},
            'vc:nok7_fc:nok9'     :{},
            'vc:nok8'             :{},
            'vc:nok8_fc:nok9'     :{},
            'vc:nok9'             :{},
        },
    ),
)
