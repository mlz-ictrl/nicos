description = 'NOK Devices for REFSANS, main file including all'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

code_base = instrument_values['code_base'] + 'optic.Optic'

includes = [
    'b1',
    'b2',
    'b3h3',
    'bs1',
    'nok2',
    'nok3',
    'nok4',
    'disc3',
    'disc4',
    'nok5a',
    'nok5b',
    'nok6',
    'nok7',
    'nok8',
    'nok9',
    'sc2',
    'zb0',
    'zb1',
    'zb2',
    'zb3',
    'primary_aperture',
    'last_aperture',
]

devices = dict(
    optic = device(code_base,
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
            'b1'    : [  -1.0,        0.0],             #04
            'nok5a' : [   0.0,        0.0],             #05
            'zb0'   :     0.0,                          #06
            'nok5b' : [   0.0,        0.0],             #07
            'zb1'   :     0.0,                          #08
            'nok6'  : [   0.0,        0.0],             #09
            'zb2'   :     0.0,                          #10
            'nok7'  : [   0.0,        0.0],             #11
            'zb3'   : [  12.0,        0.0],             #12
            'nok8'  : [   0.0,        0.0],             #13
            'bs1'   : [  12.0,        0.0],             #14
            'nok9'  : [   0.0,        0.0],             #15
            'sc2'   :     0.0,                          #16
            'b2'    : [  -1.0,        0.0],             #17
            'b3'    : [   0.0,        0.0],             #18
            },
         '12mrad_b3_789'   :{
            #'disk4' : 0.0,                          #
            #'disk3' : 0.0,                          #
            'nok2'  : [   0.0,        0.0],             #01
            'nok3'  : [   0.0,        0.0],             #02
            'nok4'  : [   0.0,        0.0],             #03
            'b1'    : [  -1.0,        0.0],             #04
            'nok5a' : [   0.0,        0.0],             #05
            'zb0'   :     0.0,                          #06
            'nok5b' : [   0.0,        0.0],             #07
            'zb1'   :     0.0,                          #08
            'nok6'  : [   0.0,        0.0],             #09
            'zb2'   :     0.0,                          #10
            'nok7'  : [  -1.244343,  -5.384393],        #11
            'zb3'   : [12.08400403, -1.6728803],        #12
            'nok8'  : [  -8.474430, -10.754457],        #13
            'bs1'   : [  12.066003, -12.719411],        #14
            'nok9'  : [ -15.791558, -19.862153],        #15
            'sc2'   :   -23.369922,                     #16
            'b2'    : [  -0.819991, -28.194153],        #17
            'b3'    : [   0.120006, -31.464310],        #18
            },
         '12mrad_b3_12.000'    :{
            #'disk4' : -12.468598498473538,                          #
            #'disk3' : -12.048578337312254,                          #
            'nok2'  : [  -0.470934,  -1.529946],        #01
            'nok3'  : [  -3.005964,  -4.805986],        #02
            'nok4'  : [  -6.882011, -11.082061],        #03
            'b1'    : [  -1.0,      -12.645607],        #04 12.090004320248847
            'nok5a' : [ -21.517249, -30.517249],        #05
            'zb0'   :   -33.583612             ,        #06
            'nok5b' : [ -36.877770, -51.518473],        #07
            'zb1'   :   -54.392610             ,        #08
            'nok6'  : [ -57.686769, -72.327472],        #09
            'zb2'   :   -75.213610             ,        #10
            'nok7'  : [ -79.023793, -87.304190],        #11
            'zb3'   : [  12.084004, -90.208330],        #12
            'nok8'  : [ -93.484487, -98.044706],        #13
            'bs1'   : [  12.066003,-101.254860],        #14
            'nok9'  : [-104.327008,-108.397603],        #15
            'sc2'   :  -111.905371,                     #16
            'b2'    : [  -1.0     ,-116.729603],        #17 12.180008640497693
            'b3'    : [  -1.0,      -60.2     ],        #18
            },

         '12mrad_b3_13.268'    :{
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [  -1.541887,  -3.532116],        #02
            'nok4'  : [  -5.827513, -10.471382],        #03
            'b1'    : [  -1.0,      -11.686477],        #04   12.099516
            'nok5a' : [ -21.971213, -30.971213],        #05
            'zb0'   :   -34.837178             ,        #06
            # Due to a mechanical limit the values are reduced by 1
            # normally the values should be:
            # 'nok5b' : [ -38.479458, -54.667368],      #07
            'nok5b' : [ -37.479458, -53.667368],        #07
            'zb1'   :   -57.845240             ,        #08
            'nok6'  : [ -61.487520, -77.675430],        #09
            'zb2'   :   -80.866571             ,        #10
            'nok7'  : [ -85.079409, -94.234866],        #11
            'zb3'   : [  12.092881, -97.445910],        #12
            'nok8'  : [-101.068287,-106.110423],        #13
            'bs1'   : [  12.072978,-109.659821],        #14
            # Due to a mechanical limit the values are reduced by 1.5
            # normally the values should be:
            # 'nok9'  : [-113.056628,-117.557398],        #15
            'nok9'  : [-111.556628,-115.057398],        #15
            'sc2'   :  -121.435862             ,        #16
            'b2'    : [  -1.0,     -126.769911],        #17   12.199032
            'b3'    : [   0.0,        0.0],             #18
            },
        '12mrad_b2_12.254_eng'    :{
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [  -1.882604,  -3.720727],        #02
            'nok4'  : [  -5.840696, -10.129650],        #03
            'b1'    : [  -1.0,      -10.793251],        #04   12.091910
            'nok5a' : [ -19.947954, -28.947954],        #05
            'zb0'   :   -32.174487             ,        #06
            'nok5b' : [ -35.538379, -50.489007],        #07
            'zb1'   :   -53.423987             ,        #08
            'nok6'  : [ -56.787878, -71.738507],        #09
            'zb2'   :   -74.685741             ,        #10
            'nok7'  : [ -78.576581, -87.032264],        #11
            'zb3'   : [  12.085782, -89.997881],        #12
            'nok8'  : [ -93.343390, -98.000143],        #13
            'bs1'   : [  12.067400,-101.278252],        #14
            'nok9'  : [-104.415433,-108.572198],        #15
            'sc2'   :  -112.154222             ,        #16
            'b2'    : [  -1.0,     -117.080576],        #17   12.183819
            'b3'    : [   0.0,        0.0],             #18
            },
        '12mrad_b2_12.88_big'    :{
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [  -1.672260,  -3.604287],        #02
            'nok4'  : [  -5.832558, -10.340620],        #03
            'b1'    : [  -1.0,      -11.344687],        #04   12.096605
            'nok5a' : [ -21.197021, -30.197021],        #05
            'zb0'   :   -33.818310             ,        #06
            'nok5b' : [ -37.354066, -53.068535],        #07
            'zb1'   :   -56.153465             ,        #08
            'nok6'  : [ -59.689221, -75.403690],        #09
            'zb2'   :   -78.501501             ,        #10
            'nok7'  : [ -82.591127, -91.478819],        #11
            'zb3'   : [  12.090165, -94.595951],        #12
            'nok8'  : [ -98.112385,-103.007056],        #13
            'bs1'   : [  12.070844,-106.452647],        #14
            'nok9'  : [-109.750109,-114.119247],        #15
            'sc2'   :  -117.884279             ,        #16
            'b2'    : [  -1.0,     -123.062325],        #17   12.193211
            'b3'    : [   0.0,        0.0],             #18
            },
        '48mrad'              :{
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [   0.000000,   0.000000],        #02
            'nok4'  : [   0.000000,   0.000000],        #03
            'b1'    : [  -1.000000,   0.000000],        #04   12.0
            'nok5a' : [   0.000000,   0.000000],        #05
            'zb0'   :     0.000000             ,        #06
            'nok5b' : [   0.000000,   0.000000],        #07
            'zb1'   :     0.000000             ,        #08
            'nok6'  : [   0.000000,   0.000000],        #09
            'zb2'   :     0.000000             ,        #10
            'nok7'  : [  -1.858601, -10.138999],        #11
            'zb3'   : [  12.168032, -14.088305],        #12
            'nok8'  : [ -24.358282, -38.044194],        #13
            'bs1'   : [  12.264203, -47.176917],        #14
            'nok9'  : [ -59.474363, -75.768478],        #15
            'sc2'   :   -89.809664             ,        #16
            'b2'    : [  -1.0,     -109.120497],        #17   12.720553
            'b3'    : [  -1.0,      -62.2],             #18
            },

        '54mrad'              :{
            # 'disk4' : 0.0,
            # 'disk3' : 0.0,
            'nok2'  : [   0.000000,   0.000000],        #01
            'nok3'  : [   0.000000,   0.000000],        #02
            'nok4'  : [   0.000000,   0.000000],        #03
            'b1'    : [  -1.000000,   0.000000],        #04   12.0
            'nok5a' : [   0.000000,   0.000000],        #05
            'zb0'   :     0.000000             ,        #06
            'nok5b' : [   0.000000,   0.000000],        #07
            'zb1'   :     0.000000             ,        #08
            'nok6'  : [   0.000000,   0.000000],        #09
            'zb2'   :     0.000000             ,        #10
            'nok7'  : [-1.34086695, -10.656433],        #11
            'zb3'   : [  12.189046, -15.850152],        #12
            'nok8'  : [-26.6536288, -42.052049],        #13
            'bs1'   : [12.29728902, -53.080527],        #14
            'nok9'  : [ -66.917980, -85.252604],        #15
            'sc2'   : -101.0521646             ,        #16
            'b2'    : [  -1.0,     -122.781289],        #17   12.810788239415222
            'b3'    : [  -1.0,      -77.2],             #18   12.540525492943482
            },

        },
        masks = {
            'debug'               :{'nok2':'ng','nok3':'debug','nok4':'debug','b1': 'debug','nok5a': 'debug','zb0': 'debug','nok5b': 'debug','zb1': 'debug','nok6': 'debug','zb2': 'debug','nok7': 'debug','zb3': 'debug','nok8': 'debug','bs1': 'debug','nok9': 'debug','b2': 'debug','b3': 'debug'},
            'gisans'              :{'nok2':'ng','nok3':   'ng','nok4':   'rc','b1':'gisans','nok5a':    'fc','zb0':'gisans','nok5b':    'fc','zb1':'gisans','nok6':    'fc','zb2':'gisans','nok7':    'fc','zb3':'gisans','nok8':    'fc','bs1':'gisans','nok9':    'fc','b2':'gisans','b3':  'slit'},
            'gisans789'           :{'nok2':'ng','nok3':   'ng','nok4':   'rc','b1':'gisans','nok5a':    'fc','zb0':'gisans','nok5b':    'fc','zb1':'gisans','nok6':    'fc','zb2':'gisans','nok7':    'ng','zb3':'gisans','nok8':    'ng','bs1':'gisans','nok9':    'fc','b2':'gisans','b3':  'slit'},
            'point'               :{'nok2':'ng','nok3':   'rc','nok4':   'ng','b1':  'slit','nok5a':    'fc','zb0':  'slit','nok5b':    'fc','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'fc','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'fc:nok5a'            :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'fc','zb0':  'slit','nok5b':    'fc','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'fc','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            '12mrad789'           :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'fc','zb0':  'slit','nok5b':    'fc','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'ng','zb3':  'slit','nok8':    'ng','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            '48mrad'              :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'vc','zb0':  'slit','nok5b':    'vc','zb1':  'slit','nok6':    'vc','zb2':  'slit','nok7':    'ng','zb3':  'slit','nok8':    'ng','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'fc:nok5b'            :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'ng','zb0':  'slit','nok5b':    'fc','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'fc','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'fc:nok6'             :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'ng','zb0':  'slit','nok5b':    'ng','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'fc','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'fc:nok7'             :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'ng','zb0':  'slit','nok5b':    'ng','zb1':  'slit','nok6':    'ng','zb2':  'slit','nok7':    'fc','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'fc:nok8'             :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'ng','zb0':  'slit','nok5b':    'ng','zb1':  'slit','nok6':    'ng','zb2':  'slit','nok7':    'ng','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'fc:nok9'             :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'ng','zb0':  'slit','nok5b':    'ng','zb1':  'slit','nok6':    'ng','zb2':  'slit','nok7':    'ng','zb3':  'slit','nok8':    'ng','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'neutronguide'        :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'ng','zb0':  'slit','nok5b':    'ng','zb1':  'slit','nok6':    'ng','zb2':  'slit','nok7':    'ng','zb3':  'slit','nok8':    'ng','bs1':  'slit','nok9':    'ng','b2':  'slit','b3':  'slit'},
            'vc:nok5a_fc:nok5b'   :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'vc','zb0':  'slit','nok5b':    'fc','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'fc','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'vc:nok5a_fc:nok6'    :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'vc','zb0':  'slit','nok5b':    'vc','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'fc','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'vc:nok5a_fc:nok7'    :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'vc','zb0':  'slit','nok5b':    'vc','zb1':  'slit','nok6':    'vc','zb2':  'slit','nok7':    'fc','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'vc:nok5a_fc:nok8'    :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'vc','zb0':  'slit','nok5b':    'vc','zb1':  'slit','nok6':    'vc','zb2':  'slit','nok7':    'vc','zb3':  'slit','nok8':    'fc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'vc:nok5a_fc:nok9'    :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'vc','zb0':  'slit','nok5b':    'vc','zb1':  'slit','nok6':    'vc','zb2':  'slit','nok7':    'vc','zb3':  'slit','nok8':    'vc','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
            'vc:nok5a'            :{'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'vc','zb0':  'slit','nok5b':    'vc','zb1':  'slit','nok6':    'vc','zb2':  'slit','nok7':    'vc','zb3':  'slit','nok8':    'vc','bs1':  'slit','nok9':    'vc','b2':  'slit','b3':  'slit'},
            #'vc:nok5b_fc:nok6'    :
            #'vc:nok5b_fc:nok7'    :
            #'vc:nok5b_fc:nok8'    :
            #'vc:nok5b_fc:nok9'    :
            #'vc:nok5b'            :
            #'vc:nok6_fc:nok7'     :
            #'vc:nok6_fc:nok8'     :
            #'vc:nok6_fc:nok9'     :
            #'vc:nok6'             :
            #'vc:nok7_fc:nok8'     :
            #'vc:nok7_fc:nok9'     :
            #'vc:nok7'             :
            #'vc:nok8_fc:nok9'     :
            #'vc:nok8'             :
            #'vc:nok9'             :
        },
    ),
)
