# pylint: skip-file

printinfo('die werte der potis statt spline WICHTIG!')
# user ++
# user --

from nicos import session
from numpy import array
from nicos.core import status as ncstatus

import time

Elemente = [
          # 'shutter_gamma',      # 1
          'nok2',               # 2
          'nok3',               # 3
          'nok4',               # 4
          # 'disc3',             # 5
          # 'disc4',             # 6
          # 'b1',                # 7
          # 'nok5a',             # 8
          # 'zb0',               # 9
          # 'nok5b',             # 10
          # 'zb1',               # 11
          'nok6',               # 12
          'zb2',                # 13
          'nok7',               # 14
          'zb3',                # 15
          'nok8',               # 16
          'bs1',                # 17
          'nok9',               # 18
          # 'sc2',               # 19
          # 'b2',                # 20
          # 'b3h3',              #
          # 'primary_aperture',  #
          # 'last_aperture',     #
        ]

test_dic = {
    'null': {
        'shutter_gamma': 0.0,
        'nok2r': 0.0,
        'nok2s': 0.0,
        'nok3r': 0.0,
        'nok3s': 0.0,
        'nok4r': 0.0,
        'nok4s': 0.0,
        'nok6r': 0.0,
        'nok6s': 0.0,
        'zb2': 0.0,
        'nok7r': 0.0,
        'nok7s': 0.0,
        'zb3r': 0.0,
        'zb3s': 0.0,
        'nok8r': 0.0,
        'nok8s': 0.0,
        'bs1r': 0.0,
        'bs1s': 0.0,
        'nok9r': 0.0,
        'nok9s': 0.0,
    },
    'neutronguide_horizontal': {
        'shutter_gamma': -0.12,
        'nok2r': -0.04,
        'nok2s': 0.08,
        'nok3r': 0.01,
        'nok3s': 0.05,
        'nok4r': -0.03,
        'nok4s': 0.08,
        'nok6r': -0.48,
        'nok6s': -0.31,
        'zb2': -1.94,
        'nok7r': -0.84,
        'nok7s': -0.89,
        'zb3r': -1.21,
        'zb3s': 0.23,
        'nok8r': -0.45,
        'nok8s': -0.55,
        'bs1r': -1.11,
        'bs1s': -1.01,
        'nok9r': -0.62,
        'nok9s': -0.61,
    },
}


def ana_avg_read(Elemente, anz, pause, tag='analog'):
    print('ana_pos ana_avg_read tag {0:s}'.format(tag))
    dic = {}
    for ele in Elemente:
        tmp = ele+'_%s' % tag
        if tmp in session.devices.keys():
            dic[ele] = []
        else:
            dic[ele+'r'] = []
            dic[ele+'s'] = []
    printinfo("ana_avg_read {0:d}x{1:.4f}sec={2:.4f}sec {3:.4f}Elemente".format(anz, pause, anz * pause, len(dic)))
    for i in range(anz):
        for ele in dic.keys():
            dic[ele].append(session.devices[ele+'_%s' % tag].read(0))
        line = ''
        sleep(pause)
    printinfo("{0:6s} {1:9s} +/- {2:s}".format('ele', 'abspos', 'std'))
    for lable in dic.keys():
        dic[lable] = array(dic[lable])
        mean = dic[lable].mean()
        printinfo("{0:6s} {1:9.5f} +/- {2:.5f}".format(lable, mean, dic[lable].std()))
        dic[lable] = mean
    return dic


class cl_ana_pos():

    _Elemente = Elemente
    history = []
    lines = []

# 2021-05-19 10:52:52         pri                                               n2                                n3                                n4         b1  5a zb0 5b zb1      n6                      zb2                       n7                      zb3                                        n8                      bs1                                         n9
    _ana_pos  = {
       # '12mrad234_12mrad_b2_12.254_eng'  : {                            'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'fc','zb0':  'slit','nok5b':    'fc','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'ng','zb3':  'slit','nok8':    'ng','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
       # '12mrad234_12mrad_b2_12.88_big'   : {                            'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'fc','zb0':  'slit','nok5b':    'fc','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'ng','zb3':  'slit','nok8':    'ng','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
       # '12mrad234_12mrad_b3_13.268'      : {                            'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'fc','zb0':  'slit','nok5b':    'fc','zb1':  'slit','nok6':    'fc','zb2':  'slit','nok7':    'ng','zb3':  'slit','nok8':    'ng','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},
       # '48mrad_54mrad'                   : {                            'nok2':'ng','nok3':   'ng','nok4':   'ng','b1':  'slit','nok5a':    'vc','zb0':  'slit','nok5b':    'vc','zb1':  'slit','nok6':    'vc','zb2':  'slit','nok7':    'ng','zb3':  'slit','nok8':    'ng','bs1':  'slit','nok9':    'fc','b2':  'slit','b3':  'slit'},

       'neutronguide_horizontal'         : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': -0.84, 'nok7s': -0.89, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': -0.45, 'nok8s': -0.55, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': -0.62, 'nok9s': -0.61, },
       '12mrad789_12mrad_b3_789'         : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':  -1.94, 'nok7r': -0.84, 'nok7s': -0.89, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': -0.45, 'nok8s': -0.55, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': -0.61, 'nok9s': -0.61, },
       'vc:nok9_horizontal'              : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': -0.84, 'nok7s': -0.89, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': -0.45, 'nok8s': -0.55, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 36.83, 'nok9s': 36.80, },
       'vc:nok8_horizontal'              : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': -0.84, 'nok7s': -0.89, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 36.83, 'nok9s': 36.80, },
       'vc:nok7_horizontal'              : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 36.83, 'nok9s': 36.80, },
       'vc:nok5a_horizontal'             : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 36.83, 'nok9s': 36.80, },
       'vc:nok5b_horizontal'             : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 36.83, 'nok9s': 36.80, },
       'vc:nok6_horizontal'              : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 36.83, 'nok9s': 36.80, },
       'fc:nok9_horizontal'              : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': -0.84, 'nok7s': -0.89, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': -0.45, 'nok8s': -0.55, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'gisans789_12mrad_b3_789'         : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':-121.86, 'nok7r': -0.84, 'nok7s': -0.89, 'zb3r':-109.99, 'zb3s':  0.23, 'nok8r': -0.45, 'nok8s': -0.55, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok8_fc:nok9_horizontal'      : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': -0.84, 'nok7s': -0.89, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok7_fc:nok9_horizontal'      : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok5a_fc:nok9_horizontal'     : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok5b_fc:nok9_horizontal'     : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok6_fc:nok9_horizontal'      : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 36.89, 'nok8s': 36.89, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'fc:nok8_horizontal'              : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': -0.84, 'nok7s': -0.89, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok7_fc:nok8_horizontal'      : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok5a_fc:nok8_horizontal'     : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok5b_fc:nok8_horizontal'     : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok6_fc:nok8_horizontal'      : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 36.55, 'nok7s': 36.69, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'fc:nok7_horizontal'              : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': -0.48, 'nok6s': -0.31, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok5a_fc:nok7_horizontal'     : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok5b_fc:nok7_horizontal'     : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok6_fc:nok7_horizontal'      : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'fc:nok5a_horizontal'             : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'fc:nok5b_horizontal'             : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'fc:nok6_horizontal'              : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'point_horizontal'                : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r': 22.71, 'nok3s': 22.43, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok5a_fc:nok5b_horizontal'    : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok5a_fc:nok6_horizontal'     : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'vc:nok5b_fc:nok6_horizontal'     : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':  -1.94, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':  -1.21, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r':  -1.11, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       'gisans_horizontal'               : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': 22.60, 'nok4s': 22.47, 'nok6r': 51.50, 'nok6s': 51.64, 'zb2':-121.86, 'nok7r': 51.13, 'nok7s': 51.11, 'zb3r':-109.99, 'zb3s':  0.23, 'nok8r': 50.46, 'nok8s': 50.44, 'bs1r': -40.95, 'bs1s':  -1.01, 'nok9r': 48.85, 'nok9s': 48.85, },
       #'48mrad_48mrad'                   : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': -2.70, 'nok7s':-10.99, 'zb3r': -15.19, 'zb3s':-13.97, 'nok8r':-25.03, 'nok8s':-38.80, 'bs1r': -48.18, 'bs1s': -48.22, 'nok9r':-10.60, 'nok9s':-27.03, },
       #'12mrad234_12mrad_b3_12.000'      : {'shutter_gamma': -0.13, 'nok2r': -0.52, 'nok2s': -1.46, 'nok3r': -2.98, 'nok3s': -4.77, 'nok4r': -6.80, 'nok4s':-11.17, 'nok6r': -6.11, 'nok6s':-20.58, 'zb2': -77.01, 'nok7r':-27.82, 'nok7s':-36.21, 'zb3r': -91.87, 'zb3s':-89.96, 'nok8r':-43.11, 'nok8s':-47.78, 'bs1r':-102.38, 'bs1s':-102.23, 'nok9r':-55.48, 'nok9s':-59.62, },
       #'reference'                       : {'shutter_gamma':-14.68, 'nok2r':-17.09, 'nok2s':-18.11, 'nok3r': 20.80, 'nok3s':  9.49, 'nok4r': 20.23, 'nok4s':  9.17, 'nok6r': 45.56, 'nok6s': 46.80, 'zb2':  68.27, 'nok7r': 62.40, 'nok7s': 66.79, 'zb3r':  72.74, 'zb3s':105.75, 'nok8r': 81.03, 'nok8s': 85.46, 'bs1r': -41.83, 'bs1s':  89.54, 'nok9r':103.05, 'nok9s': 86.78, },
       # 2024-03-22 09:52:59 gap
       '48mrad_48mrad'                   : {'shutter_gamma': -0.12, 'nok2r': -0.04, 'nok2s':  0.08, 'nok3r':  0.01, 'nok3s':  0.05, 'nok4r': -0.03, 'nok4s':  0.08, 'nok6r': 36.95, 'nok6s': 37.08, 'zb2':  -1.94, 'nok7r': -2.70, 'nok7s':-10.99, 'zb3r':  -9.19, 'zb3s':-19.97, 'nok8r':-25.03, 'nok8s':-38.80, 'bs1r': -42.18, 'bs1s': -54.22, 'nok9r':-10.60, 'nok9s':-27.03, },
       '12mrad234_12mrad_b3_12.000'      : {'shutter_gamma': -0.13, 'nok2r': -0.52, 'nok2s': -1.46, 'nok3r': -2.98, 'nok3s': -4.77, 'nok4r': -6.80, 'nok4s':-11.17, 'nok6r': -6.11, 'nok6s':-20.58, 'zb2': -77.01, 'nok7r':-27.82, 'nok7s':-36.21, 'zb3r': -85.87, 'zb3s':-95.96, 'nok8r':-43.11, 'nok8s':-47.78, 'bs1r': -96.38, 'bs1s':-108.23, 'nok9r':-55.48, 'nok9s':-59.62, },
       'reference'                       : {'shutter_gamma':-14.68, 'nok2r':-17.09, 'nok2s':-18.11, 'nok3r': 20.80, 'nok3s':  9.49, 'nok4r': 20.23, 'nok4s':  9.17, 'nok6r': 45.56, 'nok6s': 46.80, 'zb2':  68.27, 'nok7r': 62.40, 'nok7s': 66.79, 'zb3r':  78.74, 'zb3s': 99.75, 'nok8r': 81.03, 'nok8s': 85.46, 'bs1r': -35.83, 'bs1s':  83.54, 'nok9r':103.05, 'nok9s': 86.78, },

  }

    def make_line(self, pos_tag=None, force=False):
        state = optic.status(0)
        if state[0] != ncstatus.OK:
            printinfo(state)
            printwarning('no numerical check')
            if force:
                printwarning('but force')
            else:
                return state[1]
        if pos_tag is None:
            pos_tag = optic.mode + '+' + optic.read(1)
        printinfo(pos_tag)
        self.akt_dic = ana_avg_read(self._Elemente, anz=100, pause=.6, tag='analog')
        line = ""
        line += "  '"
        line += pos_tag
        line += "'" + (35 - len(line)) * " "
        line += ":{"
        for tag in self._Elemente:
            if tag in self.akt_dic.keys():
                line += "'%s': %7.2f, " % (tag, self.akt_dic[tag])
            else:
                for sufix in ['r', 's']:
                    line += "'%s': %7.2f, " % (tag + sufix, self.akt_dic[tag + sufix])
        line += "}, ###" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return line

    def line_dic(self, dic):
        line = '{'
        for lable in self._Elemente:
            if lable in dic.keys():
                line += "'%s':%10.4f, " % (lable, dic[lable])
            else:
                for pos in ['r', 's']:
                    line += "'%s%s':%10.4f, " % (lable, pos, dic[lable+pos])
        line += '}'
        return line

    def check(self, Elemente=None, pos_tag=None, force=False, anz=100, Debug=False, limit=1.0, extra=5):
        fail = False

        if Elemente is None:
            Elemente = self._Elemente

        for sele in Elemente:
            if sele in session.devices.keys():
                state = session.devices[sele].status(0)
                if state[0] != ncstatus.OK:
                    printinfo('%s %s' % (sele, state[1]))
                    fail = True
            else:
                printinfo('not in session %s' % sele)
        if fail:
            printwarning('no numerical check')
            if force:
                printwarning('but force')
            else:
                return -1
                return state[1]
        if pos_tag is None:
            pos_tag = optic.mode + '+' + str(optic.read(0))
        elif pos_tag == 'status':
            return 0
        printinfo('pos_tag: %s' % pos_tag)

        self.akt_dic = ana_avg_read(Elemente, anz=anz, pause=.6, tag='analog')
        line = ""
        line += "  '"
        line += pos_tag
        line += "'" + (35 - len(line)) * " "
        line += ":{"
        for tag in Elemente:
            if tag in self.akt_dic.keys():
                line += "'%s': %7.2f, " % (tag, self.akt_dic[tag])
            else:
                for sufix in ['r', 's']:
                    line += "'%s': %7.2f, " % (tag + sufix, self.akt_dic[tag + sufix])
        line += "}, ###" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        printinfo(line)
        self.lines.append(line)

        if pos_tag not in self._ana_pos.keys():
            printinfo('new tag %s' % pos_tag)
            printinfo(self.line_dic(self.akt_dic))
            self._ana_pos[pos_tag] = self.akt_dic.copy()
            return 0
        else:
            printinfo('tag %s' % pos_tag)
            self.history.append({
                    'tag': pos_tag,
                    'werte': [],
                    'date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    })
            for ele in self.akt_dic.keys():
                dif = abs(self._ana_pos[pos_tag][ele] - self.akt_dic[ele])
                self.history[-1]['werte'].append(['%07.3f' % dif, ele])
            self.history[-1]['werte'].sort()
            self.history[-1]['werte'].reverse()
            printinfo(self._history_line(self.history[-1]))
            res = float(self.history[-1]['werte'][0][0])
            if res > limit:
                printerror('limit exedet')
                evels = []
                limit /= extra
                index = 0
                while True:
                    evel = self.history[-1]['werte'][index][1]
                    for ch in ['s', 'r']:
                        if evel[-1] == ch:
                            evel = evel[:-1]
                            break
                    if evel not in evels:
                        evels.append(evel)
                    index += 1
                    if Debug:
                        printinfo(index, evels)
                    if (index >= len(self.history[-1]['werte'])) or (limit > float(self.history[-1]['werte'][index][0])):
                        break
                res = evels
            return res

    def check_old(self, pos_tag=None, force=False, anz=100, Debug=False, limit=1.0):
        fail = False
        for sele in self._Elemente:
            if sele in session.devices.keys():
                state = session.devices[sele].status(0)
                if state[0] != ncstatus.OK:
                    printinfo('%s %s' % (sele, state[1]))
                    fail = True
            else:
                printinfo('not in session %s' % sele)
        if fail:
            printwarning('no numerical check')
            if force:
                printwarning('but force')
            else:
                return -1
                return state[1]
        if pos_tag is None:
            pos_tag = optic.mode + '+' + str(optic.read(0))
        elif pos_tag == 'status':
            return 0
        printinfo('pos_tag: %s' % pos_tag)
        self.akt_dic = ana_avg_read(self._Elemente, anz=anz, pause=.6, tag='analog')

        line = ""
        line += "  '"
        line += pos_tag
        line += "'" + (35 - len(line)) * " "
        line += ":{"
        for tag in self._Elemente:
            if tag in self.akt_dic.keys():
                line += "'%s': %7.2f, " % (tag, self.akt_dic[tag])
            else:
                for sufix in ['r', 's']:
                    line += "'%s': %7.2f, " % (tag + sufix, self.akt_dic[tag + sufix])
        line += "}, ###" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        printinfo(line)
        self.lines.append(line)

        if pos_tag not in self._ana_pos.keys():
            printinfo('new tag %s' % pos_tag)
            printinfo(self.line_dic(self.akt_dic))
            self._ana_pos[pos_tag] = self.akt_dic.copy()
            return 0
        else:
            printinfo('tag %s' % pos_tag)
            self.history.append({
                    'tag': pos_tag,
                    'werte': [],
                    'date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    })
            for ele in self.akt_dic.keys():
                dif = abs(self._ana_pos[pos_tag][ele] - self.akt_dic[ele])
                self.history[-1]['werte'].append(['%07.3f' % dif, ele])
            self.history[-1]['werte'].sort()
            self.history[-1]['werte'].reverse()
            printinfo(self._history_line(self.history[-1]))
            return float(self.history[-1]['werte'][0][0])

    def _history_line(self, data):
        line = ''
        # line += '%s: %s ' % ('date', data['date'])
        line += '%s: %30s ' % ('tag', data['tag'])
        for item in data['werte']:
            line += item[0] + ' ' + item[1] + ' '
        # printinfo('_history_line: ' + line)
        return line

    def status(self):
        for data in self.history:
            printinfo(self._history_line(data))
        printinfo('datas %d' % len(self.history))

    def best_of(self, dic=None):
        anz = 1
        res = {}
        printinfo('best_of', anz)

        if dic is None:
            self.akt_dic = ana_avg_read(self._Elemente, anz=anz, pause=.6, tag='analog')
            printinfo('best_of autoread done')
        else:
            self.akt_dic = dic

        for pos_tag in self._ana_pos:
            printinfo('tag %s' % pos_tag)
            self.history.append({
                    'tag': pos_tag,
                    'werte': [],
                    })
            for ele in self.akt_dic.keys():
                # printinfo('{0:14s} {1:6.2f} {2:6.2f}'.format(ele,self._ana_pos[pos_tag][ele],self.akt_dic[ele][0]))
                # dif = abs(self._ana_pos[pos_tag][ele] - self.akt_dic[ele][0])
                dif = abs(self._ana_pos[pos_tag][ele] - self.akt_dic[ele])
                self.history[-1]['werte'].append(['%07.3f' % dif, ele])
            self.history[-1]['werte'].sort()
            self.history[-1]['werte'].reverse()
            # printinfo(self.history[-1]['werte'][0][0])
            res[pos_tag] = float(self.history[-1]['werte'][0][0])
            # printinfo('break');break

        printinfo('result dic')
        mm = min(res.values())
        for tag in res:
            akt = res[tag]
            printinfo('{0:30s} {1:7.3f} {2:s}'.format(tag, akt, str(akt == mm)))
            if akt == mm:
                pos_tag = tag
        printinfo('try:', pos_tag, mm)
        for set in self.history:
            if set['tag'] == pos_tag:
                for data in set['werte']:
                    printinfo(data)
                break
        printinfo('try:', pos_tag, mm)
        return pos_tag


ana_pos = cl_ana_pos()
if True and False:
    # selbsttest
    res = []
    for tag in ana_pos._ana_pos.keys():
        res.append(str(ana_pos.best_of(ana_pos._ana_pos(tag)) == tag) + ' ' + tag)
    for line in res:
        printinfo(line)

printinfo('try: ana_pos.best_of()')
