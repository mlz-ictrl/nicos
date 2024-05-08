# pylint: skip-file

# userinterface ++
# parallel = True
# userinterface --

LDeveloping = True and False
readonly = False
analyse = True  # and False

"""
writing complex class D4A to make further user
reading elements vs read with string? read with strings: if eg _acc has been read, _motor and _poti can be scipped ### todo
"""

import threading
import time
import sys

from nicos.core import status as ncstatus
from nicos import session


def D4A_nicos(name):
    Debug = LDeveloping  # and False
    if Debug:
        printinfo('D4A_nicos >%s<' % name)
    if name in session.devices:
        try:
            rr = session.devices[name].read(0)
        except:
            rr = 'except >%s<' % str(sys.exc_info()[0])
        if Debug:
            printinfo('nicos rr ' + str(rr) + name)
        try:
            ss = session.devices[name].status(0)
        except:
            ss = 'except >%s<' % str(sys.exc_info()[0])
        if Debug:
            printinfo('nicos ss ' + str(ss) + name)
        tt = str(type(session.devices[name]))
        if Debug:
            printinfo('nicos tt ' + str(tt))
        try:
            if hasattr(session.devices[name], 'fixed'):
                ff = session.devices[name].fixed
            else:
                ff = 'no fixed'
        except:
            ff = 'ff except'
        result = {'read': rr, 'status': ss, 'type': tt, 'fix': ff}
    else:
        result = {'read': -666, 'status': [0, ' not in session.devices'], 'type': ' not in session.devices', 'fix': ' not in session.devices'}
    if Debug:
        printinfo(name + ' ' + str(result))
    return result


# Liste = list(session.devices.keys())  string
"""
"""
# bekannt = [
#     'configsink',
#     'conssink',
#     'daemonsink',
#     'email',
#     'Exp',
#     'filesink',
#     'livesink',
#     'REFSANS',
#     'smser',
#     'chopper_io',
#     ]


def _ibs_val(res, Debug=False):
    anaylse = {
        'fails': [],
        'nok': [],
        }
    bekannt = [
        'REFSANS',
        'Exp',
        'sink',
        'email',
        'smser',
        '_com',
        '_analog',
        '_axis',
        '_motor',
        '_poti',
        'ana4gpio',
        'autocollimator',
        'beamstop',
        'cache',
        'chopper',
        'cpt',
        'Crane',
        'expertvibro8',
        'image',
        'LogSpace',
        'memograph',
        'pressureventile',
        'rate',
        'real_flight_path',
        'resolution',
        'safetysystem',
        'Space',
        'resistor',
        'X16Voltage',
        'wachdog',
        'optic',
        'det_pivot',
        'det_table',
        'det_yoke_enc1',
        'det_yoke_enc2',
        'det_yoke_skew',
        ]
    sub_element = {
        '_acc': [0.0, 0.8],
        'Temp': [12, 50],
        'pt1000': [12, 50],
        'wegbox': [9.0, 10.0],
        'nok_ref': [18.0, 20.0],
        'core': [12, 25],
        'det_table': [1270, 11025],
        'hv_mon1': [649,  651],
        'hv_mon2': [734,  736],
        'hv_mon3': [859,  861],
        'hv_mon4': [1099, 1101],
        'hv_drift1': [-999, -1001],
        'hv_anode': [3099, 3101],
        'hv_drift2': [-4799, -4801],
        }
    toleranz = [-2, 2]
    sorted = list(res.keys())
    sorted.sort()
    if Debug:
        printinfo('_ibs_val begin')
        printinfo(sorted)
    for key in sorted:
        info = ''
        check = True
        nok = False

        if Debug:
            printinfo(type(res))
            printinfo('key', key)
            printinfo(type(res[key]))
            printinfo(res[key])
        val = res[key]['read']
        valt = type(val)
        ss = res[key]['status']
        ff = res[key]['fix']

        for evel in bekannt:
            if evel in key:
                check = False
                info += 'uncheck'
                # nok = True
                break
        if check:
            numeric = True
            if not ss[0] == ncstatus.OK:
                nok = True
                info += 'status'
            if str(valt) == 'readonlylist':
                nok = True
                numeric = False
                info += 'readonlylist'
            elif isinstance(valt, list):
                # nok = True
                numeric = False
                info += 'list'
            elif isinstance(valt, tuple):
                numeric = False
                # nok = True
                info += 'tuple'
            elif isinstance(valt, dict):
                numeric = False
                # nok = True
                info += 'dict'
            elif isinstance(valt, str):
                numeric = False
                # nok = True
                info += 'string'
            else:
                pass  # float int
            if ff == '':
                pass
            elif ff == 'no fixed':
                ff = ''
            else:
                nok = True
                info += 'fixed'
            if numeric:
                check_val = toleranz
                for skey in sub_element.keys():
                    if skey in key:
                        check_val = sub_element[skey]
                        break
                if check_val is None:
                    nok = False
                    info += 'None'
                else:
                    try:
                        nok = not (check_val[0] < val < check_val[1])
                        info += 'val'
                    except:
                        nok = True
                        info += str(valt)
        if nok:
            line = '{0:25s} {4:s} {1:s} {2:s} {3:s} '.format(key, info, str(ss), str(val), ff)
            anaylse['nok'].append(line)
    for tag in [
            'fails',
            'nok',
       ]:
        anaylse[tag].sort()
        printinfo(tag, len(anaylse[tag]))
        for line in anaylse[tag]:
            printinfo(line)
    printinfo('borstig', bekannt)
    printinfo('toleranz', toleranz)


def read0(
        Liste=None,
        analyse=True,
        laufzeit=False,
        Debug=False,
        show=False,
        give_return=False,
        ):
    try:
        D4A = cl_D4A()
        printinfo("    Device 'threading' created.")
    except:
        printwarning('pls run d4a.py')
        return
    D4A.info()
    print('read0')
    if Liste is None:
        Liste = list(session.devices.keys())  # elemente
    elif not isinstance(Liste, list):
        Liste = [Liste]

    if Debug:
        laufzeit = False
        printinfo(len(Liste))
        printinfo(Liste[0])
        printinfo(type(Liste[0]))
        # return 'Debug break'

    if laufzeit:
        dauer = [time.time()]
    printinfo('read %d devices parallel' % len(Liste))
#    res = D4A.nicos(Liste)
    res = D4A.execute(Order='func', method=D4A_nicos, argument=Liste)
    printinfo('result is stored in dic res with %d elements' % len(res))

    if laufzeit:
        dauer.append(time.time())

    if analyse:
        _ibs_val(res)
        if laufzeit:
            dauer.append(time.time())

    if show:
        Liste = list(res.keys())
        Liste.sort()
        for key in Liste:
            line = '%15s:  ' % key
            for tag in ['read', 'status']:
                line += '%s ' % str(res[key][tag])
            printinfo(line)

    if laufzeit:
        printinfo('dauer', dauer)
        for i in range(len(dauer) - 1):
            printinfo(dauer[i+1] - dauer[0])
        for i in range(len(dauer) - 1):
            printinfo(dauer[i+1] - dauer[i])
    if give_return:
        return res


printinfo('use read0()')

if LDeveloping and False:
    printinfo('read0 LDeveloping')
    read0([b1.name, nok2.name], show=True)
