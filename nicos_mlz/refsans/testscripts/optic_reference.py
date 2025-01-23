# pylint: skip-file

# test: subdirs = frm2
# test: setups = 07_refsans_full
# test: skip

from nicos import session
from nicos.core import status as ncstatus

# userinterface ++
tus = 'group'       # alle auf ein mal schneller
# tus = 'seriell'    # einen nach dem anderen, Diagnose!
# tus = False        # nichts tun Funktionen auffrischen!
home =      False  # bleibt nach letzer reffahrt stehen
# home = 'null'
# home = ['neutronguide', 'horizontal', 'closed']
# home = ['gisans', 'horizontal', 'closed']
# home = ['vc:nok5a', 'horizontal', 'closed']
refmove =   True  # and False  #POWER DOWN
readonly = False  # and True  #laden der funktionen
ana_pos_check = True
poti_only = False
# poti_only = 'nok3'  #2024-02-07 08:25:59 MP refswitch def!
# userinterface --

lmsg = 'optic_reference'

Elemente = [
    'shutter_gamma',
    'nok2',
    'nok3',
    'nok4',
    'nok6',
    'zb2',
    'nok7',
    'zb3',
    'nok8',
    'bs1',
    'nok9',
]

run_it = []
if ana_pos_check:
    try:
        ana_pos
    except:
        run_it.append('please run ana_pos first')
try:
    avg_read
except:
    run_it.append('please run refsans.py first')
# try:
#     lyric
# except:
#     run_it.append('please run lyric.py first')
if len(run_it) > 0:
    for line in run_it:
        printinfo(line)
    printerror('please run missing scripts')
    raise Exception('please run missing scripts')  # Kill the script

ipcsms_single = []  # single
ipcsms_double = []  # linked second
liste_beckhoff = []
ipcsms_two = []     # independend second
ipcsms_single.append('shutter_gamma')
ipcsms_double.append('nok2')
ipcsms_double.append('nok3')
ipcsms_double.append('nok4')
ipcsms_double.append('nok6')
ipcsms_single.append('zb2')
ipcsms_double.append('nok7')
ipcsms_two.append('zb3')
ipcsms_double.append('nok8')
ipcsms_two.append('bs1')
ipcsms_double.append('nok9')
liste_beckhoff.append('nok5a')
liste_beckhoff.append('nok5b')
liste_beckhoff.append('zb0')
liste_beckhoff.append('zb1')


def optic_status(Elemente=['shutter_gamma', 'nok2', 'nok3', 'nok4', 'nok6', 'zb2', 'nok7', 'zb3', 'nok8', 'bs1', 'nok9', ]):
    tag = '_motor'
    for ele in Elemente:
        stat = session.devices[ele].status(0)
        line = ''
        line += '{0:14s}'.format(ele)
        line += '{0:14s}'.format(session.devices[ele].name)
        line += '{0:4d} {1:s}'.format(*stat)
        printinfo(line)
        if ele in ipcsms_single:
            printinfo('     ipcsms_single', session.devices[ele + tag].status(0))
        if ele in ipcsms_double:
            printinfo('     ipcsms_double', session.devices[ele + 'r' + tag].status(0))
            printinfo('     ipcsms_double', session.devices[ele + 's' + tag].status(0))
        if ele in ipcsms_two:
            printinfo('     ipcsms_two', session.devices[ele + 'r' + tag].status(0))
            printinfo('     ipcsms_two', session.devices[ele + 's' + tag].status(0))


def ana_read(Elemente, tag='analog', anz=5):
    printinfo('ana read. anz = %d' % anz)
    dic = {}
    for i in range(anz):
        sleep(.6)
        for ele in Elemente:
            if ele in ipcsms_single:
                val = session.devices[ele+'_%s' % tag].read(0)
                if i == 0:
                    dic[ele] = []
                dic[ele].append(val)
            if ele in ipcsms_double + ipcsms_two:
                val = session.devices[ele+'r_%s' % tag].read(0)
                if i == 0:
                    dic[ele+'r'] = []
                dic[ele+'r'].append(val)
                val = session.devices[ele+'s_%s' % tag].read(0)
                if i == 0:
                    dic[ele+'s'] = []
                dic[ele+'s'].append(val)
    return dic


def ana_ana(dic):
    redo = []
    for tag in dic.keys():
        dif = max(dic[tag]) - min(dic[tag])
        acc = sum(dic[tag])/len(dic[tag])
        status = ''
        if dif > .1:
            status += ' invalid'
        if abs(acc) > .5:
            status += ' fail'
        printinfo('%6s %7.3f %.3f%s' % (tag, acc, dif, status))
        if len(status) > 0:
            if tag[-1] in ['r', 's']:
                redo.append(tag[:-1])
            else:
                redo.append(tag)
    return redo


def do_reference(motor):
    printinfo('%s reference status: %s' % (motor, session.devices[motor].status(0)[1]))
    if readonly:
        printinfo('BLOCKED')
    else:
        session.devices[motor].reference()


def optic_pollinterval_set(Elemente=Elemente):
    optic_pollinterval(Elemente=Elemente, pi=5)


def optic_pollinterval_clear(Elemente=Elemente):
    optic_pollinterval(Elemente=Elemente, pi=None)


def optic_pollinterval(Elemente=Elemente, pi=None):
    tags = ['_motor', '_acc']
    printinfo('optic_pollinterval %s %s' % (str(pi), str(tags)))
    for ele in Elemente:
        if ele in ipcsms_single:
            for tag in tags:
                session.devices[ele+tag].pollinterval = pi
                if pi is not None:
                    pi += 1
        if ele in ipcsms_double + ipcsms_two:
            for tag in tags:
                for ax in ['r', 's']:
                    session.devices[ele+ax+tag].pollinterval = pi
                    if pi is not None:
                        pi += 1


def optic_beckhoff_reset(Elemente=liste_beckhoff):
    for ele in Elemente:
        if ele in liste_beckhoff:
            dev = session.devices[ele]
            dev.maw(dev.read(0))
            printinfo(ele, dev.status(0))


def optic_ipcsms_reset(Elemente=Elemente, tag='ipc.NOKMotorIPC'):
    printinfo('reset controllers IPCSMS')
    res = True
    for sele in session.devices.keys():
        if tag in str(type(session.devices[sele])):
            for use in Elemente:
                if use in sele:
                    line = sele + ':' + (20 - len(sele))*' '
                    try:
                        line += 'r'
                        session.devices[sele].reset()
                        line += 's'
                        session.devices[sele].speed = session.devices[sele].speed
                        line += 'a'
                        session.devices[sele].accel = session.devices[sele].accel
                        line += 'done'
                        printinfo(line)
                    except:
                        line += 'FAIL'
                        printerror(line)
                        res = False
    return res


def optic_reset():
    optic_beckhoff_reset()
    optic_ipcsms_reset()
    try:
        stat = optic.status(0)
    except:
        stat = [ncstatus.ERROR, 'except']
    if stat[0] == ncstatus.OK:
        printinfo('Finished')
    else:
        printwarning(stat[1])
        printerror('retry tell MP!')


def optic_ipcsms_analog_setpos(Elemente=Elemente):
    printinfo('optic_ipcsms_analog_setpos')
    anas  = []
    missing = []
    Liste = session.devices.keys()
    for ele in Elemente:
        if ele in ipcsms_single:
            sele = ele + '_analog'
            if sele in Liste:
                anas.append(session.devices[sele])
            else:
                missing.append(sele)
        if ele in ipcsms_double + ipcsms_two:
            for tag in ['r', 's']:
                sele = ele + tag + '_analog'
                if sele in Liste:
                    anas.append(session.devices[sele])
                else:
                    missing.append(sele)
    if len(missing) > 0:
        printerror('missing', missing)
    res = avg_read(anas, anz=5, pause=.7, verbose=False)
    for i in range(len(anas)):
        sele = anas[i].name
        sele = sele.replace('_analog', '_motor')
        printinfo(sele + ':' + (20 - len(sele))*' ' + '%7.2f' % res[i])
        session.devices[sele].setPosition(res[i])
    return missing


def optic_ipcsms_reference(Elemente, refmove, poti_only):
    optic_pollinterval_set(Elemente=Elemente)
    pre = 2.5
    printinfo('try reset')
    if type(Elemente) == type(''):
        Elemente = [Elemente]
    printinfo(Elemente)

    try:
        optic.mode = 'neutronguide'
        wait(*Elemente)
    except:
        printwarning('optic.mode = neutronguide FAIL')
    ok = True
    printinfo('check for mode')
    for ele in Elemente:
        try:
            session.devices[ele].mode
            if session.devices[ele].mode not in ['ng', 'slit']:
                vor = session.devices[ele].mode
                if session.devices[ele].mode in ['vc', 'fc']:
                    session.devices[ele].mode = 'ng'
                printinfo(session.devices[ele].name + ' ' + vor + ' ' + session.devices[ele].mode)
                ok = False
        except:
            pass  # kein mode ist gut (shutter_gamma)
    if ok:
        printinfo('test mode success')
    else:
        printerror('test mode FAIL')
        return

    optic_ipcsms_reset(Elemente=Elemente)
    if ana_pos_check:
        if home is False:
            printwarning('no homing so no "ana_pos.check(status)"')
        else:
            printinfo('check status loop')
            fail = False
            for sele in Elemente:
                stat = session.devices[ele].status(0)
                if stat[0] != ncstatus.OK and ele != 'shutter_gamma':
                    printerror(ele, stat[1])
                    fail = True
            if fail:
                printerror('kill the skript')
                1 / 0
    lmsg = 'optic_reference ctrl_reset'

    printinfo('name analog setPositon')
    res = optic_ipcsms_analog_setpos(Elemente=Elemente)
    lmsg = 'optic_reference setPos'
    if poti_only is True:
        lmsg = 'optic_ipcsms_reference poti_only'
        printwarning(lmsg)
        return lmsg
    elif poti_only is False:
        pass
    elif isinstance(poti_only, str):
        if poti_only in Elemente:
            printwarning('poti_only %s' % poti_only)
            Elemente.remove(poti_only)
    elif isinstance(poti_only, list):
        for sele in poti_only:
            if sele in Elemente:
                printwarning('poti_only %s' % sele)
                Elemente.remove(sele)
    else:
        printerror('ill poti_only %s ' % str(poti_only))
        return poti_only

    printinfo('1. prepare')
    for ele in Elemente:
        if ele in ipcsms_double:
            prepare = session.devices[ele+'r_motor'].refpos - pre
            printinfo('%s %.1f' % (ele, prepare))
            if readonly:
                printinfo('BLOCKED')
            else:
                # session.devices[ele].reactor(prepare)        #Konzept!
                session.devices[ele].move([prepare, prepare])  # 2021-05-26 12:51:04 1Min besser!
        if ele in ipcsms_single:
            prepare = session.devices[ele+'_motor'].refpos - pre
            printinfo('%s %.1f' % (ele, prepare))
            if readonly:
                printinfo('BLOCKED')
            else:
                session.devices[ele+'_motor'].move(prepare)
        if ele in ipcsms_two:
            r_prepare = session.devices[ele+'r_motor'].refpos - pre
            s_prepare = session.devices[ele+'s_motor'].refpos - pre
            printinfo('%s %.1f %.1f' % (ele, r_prepare, s_prepare))
            if readonly:
                printinfo('BLOCKED')
            else:
                session.devices[ele+'r_motor'].move(r_prepare)
                session.devices[ele+'s_motor'].move(s_prepare)
    if len(Elemente) > 0:
        wait(*Elemente)
    lmsg = 'optic_reference 1.prepare'

    ana_read(Elemente)

    printinfo('1. Prestatustest')
    fail = False
    for ele in Elemente:
        if ele in ipcsms_double:
            tag = ele+'r_motor'
        elif ele in ipcsms_single:
            tag = ele+'_motor'
        elif ele in ipcsms_two:
            tag = ele+'r_motor'
        else:
            tag = 'FAIL'
        stat = session.devices[tag].status(0)[1]
        if 'reference switch active' in stat:
            printerror('%s for refmove %s' % (tag, stat))
            fail = True
        elif True:
            printinfo('%s %s' % (tag, stat))
    if fail:
        1 / 0
        return False

    if not refmove:
        printinfo('no refmove for PowerDown')
        return
    printinfo('1. reference')
    for ele in Elemente:
        if ele in ipcsms_double:
            do_reference(ele+'r_motor')
        if ele in ipcsms_single:
            do_reference(ele+'_motor')
        if ele in ipcsms_two:
            do_reference(ele+'r_motor')
            # do_reference(ele+'s_motor') bekannter Fehler
    if len(Elemente) > 0:
        wait(*Elemente)
    lmsg = 'optic_reference 1.reference'

    printinfo('2. prepare')
    for ele in Elemente:
        if ele in ipcsms_double:
            prepare = session.devices[ele+'s_motor'].refpos - pre
            printinfo('%s %.1f' % (ele, prepare))
            if readonly:
                printinfo('BLOCKED')
            else:
                session.devices[ele].sample(prepare)
    if len(Elemente) > 0:
        wait(*Elemente)
    lmsg = 'optic_reference 2. prepare'

    printinfo('2. Prestatustest')
    fail = False
    for ele in Elemente:
        if ele in ipcsms_double + ipcsms_two:
            tag = ele+'s_motor'
            stat = session.devices[tag].status(0)[1]
            if 'reference switch active' in stat:
                printerror('%s for refmove %s' % (tag, stat))
                fail = True
            elif True:
                printinfo('%s %s' % (tag, stat))
    if fail:
        1 / 0
        return False

    printinfo('2. reference')
    for ele in Elemente:
        if ele in ipcsms_double:
            do_reference(ele+'s_motor')
        if ele in ipcsms_two:
            do_reference(ele+'s_motor')
    if len(Elemente) > 0:
        wait(*Elemente)
    lmsg = 'optic_reference 2. reference'
    optic_pollinterval_clear(Elemente=Elemente)


def optic_home(home='null', arg=Elemente, readonly=False, ana_pos_check=ana_pos_check, Debug=False):
    line = 'home: '
    line += '%s ' % str(home)
    line += 'readonly %s ' % str(readonly)
    line += 'ana_pos_check %s ' % str(ana_pos_check)
    line += 'Debug %s ' % str(Debug)
    printinfo(line)
    printinfo(arg)
    Elemente = []
    for ele in arg:
        if ele in session.devices.keys():
            Elemente.append(ele)
            printinfo('                    use: %s' % ele)
        else:
            printwarning('not in session: %s' % ele)
    if home is False:
        printinfo('no homing')
    elif home == 'null':
        try:
            optic.mode = 'neutronguide'
        except:
            printerror('optic.mode = neutronguide FAIL')
        ok = True
        printinfo('check for mode')
        for ele in Elemente:
            try:
                session.devices[ele].mode
                if session.devices[ele].mode not in ['ng', 'slit']:
                    printerror(session.devices[ele].name + ' ' + session.devices[ele].mode)
                    ok = False
            except:
                pass  # kein mode ist gut (shutter_gamma)
        if ok:
            printinfo('test mode success')

        for ele in Elemente:
            if ele in ipcsms_double:
                prepare = 0.0
                printinfo('%s %.1f' % (ele, prepare))
                if readonly:
                    printinfo('BLOCKED')
                else:
                    session.devices[ele].move([prepare, prepare])  # 2021-05-26 12:51:04 1Min besser!
            if ele in ipcsms_single:
                prepare = 0.0
                printinfo('%s %.1f' % (ele, prepare))
                if readonly:
                    printinfo('BLOCKED')
                else:
                    session.devices[ele+'_motor'].move(prepare)
            if ele in ipcsms_two:
                r_prepare = 0.0
                s_prepare = 0.0
                printinfo('%s %.1f %.1f' % (ele, r_prepare, s_prepare))
                if readonly:
                    printinfo('BLOCKED')
                else:
                    session.devices[ele+'r_motor'].move(r_prepare)
                    session.devices[ele+'s_motor'].move(s_prepare)
        if len(Elemente) > 0:
            wait(*Elemente)
    else:
        printinfo('home, this is global for all elements neutronguide horizontal')
        if readonly:
            printinfo('BLOCKED')
        else:
            shutter_gamma.move(home[2])
            optic.mode = home[0]
            if len(Elemente) > 0:
                wait(*Elemente)
            optic.maw(home[1])
            if ana_pos_check:
                ana_pos.check()


def optic_reference(
    Elemente=Elemente,
    home=home,
    refmove=True,
    readonly=False,  # and True  #laden der funktionen
    ana_pos_check=ana_pos_check,
    tus='group',
    poti_only=poti_only,
    error='raise',
   ):

    line = 'optic_reference: '
    line += 'home %s ' % str(home)
    line += 'refmove %s ' % str(refmove)
    line += 'readonly %s ' % str(readonly)
    line += 'ana_pos_check %s ' % str(ana_pos_check)
    line += 'tus %s ' % str(tus)
    line += 'poti_only %s ' % str(poti_only)
    printinfo(line)
    printinfo(Elemente)
    if refmove is False:
        ana_pos_check = False
        home = False
    if poti_only is not False:
        ana_pos_check = False
        printwarning('poti_only != False: no ana_pos_check')

    if not isinstance(Elemente, list):
        Elemente = [Elemente]
    for i in range(len(Elemente)):
        if not isinstance(Elemente[i], str):
            Elemente[i] = Elemente[i].name

    if tus == 'group':
        printinfo(optic_ipcsms_reference(Elemente=Elemente, refmove=refmove, poti_only=poti_only))
    elif tus == 'seriell':
        for ele in Elemente:
            printinfo(optic_ipcsms_reference(Elemente=[ele], refmove=refmove, poti_only=poti_only))
    else:
        pass

    printinfo('  analyse1')
    res = ana_ana(ana_read(Elemente, tag='acc'))
    if len(res) > 0:
        printerror(res)
        if ana_pos_check:
            printerror('ana_pos_check fail')
            if error == 'raise':
                raise Exception('ana_pos_check failed')  # Kill the script
            elif error == 'retry':
                if tus == 'group':
                    printinfo(optic_ipcsms_reference(Elemente=res, refmove=refmove, poti_only=poti_only))
                elif tus == 'seriell':
                    for ele in res:
                        printinfo(optic_ipcsms_reference(Elemente=[ele], refmove=refmove, poti_only=poti_only))
                else:
                    pass
                res = ana_ana(ana_read(Elemente, tag='acc'))
                if len(res) > 0:
                    printerror(res)
                    if ana_pos_check:
                        raise Exception('ana_pos_check failed')  # Kill the script
            elif error == 'return':
                return res
            else:
                printerror(error, 'unknown')
                raise Exception('Unknown')  # Kill the script
        else:
            printinfo('but no ana_pos_check')
    printinfo('  analyse4')

    if ana_pos_check:
        res = ana_pos.check(Elemente=Elemente, pos_tag='reference', force=True)
        printinfo(res)
        if res < 0:
            printerror('not ref')
            if error == 'raise':
                raise Exception('not ref')  # Kill the script
            elif error == 'retry':
                if tus == 'group':
                    printinfo(optic_ipcsms_reference(Elemente=Elemente, refmove=refmove, poti_only=poti_only))
                elif tus == 'seriell':
                    for ele in Elemente:
                        printinfo(optic_ipcsms_reference(Elemente=[ele], refmove=refmove, poti_only=poti_only))
                else:
                    pass
                res = ana_pos.check(Elemente=Elemente, pos_tag='reference')
                printinfo(res)
                if res < 0:
                    printerror('not ref')
                    raise Exception('not ref')
            elif error == 'return':
                return Elemente
            else:
                printerror(error, 'unknown')
                raise Exception('unknown')  # Kill the script
    optic_home(home, arg=Elemente, readonly=readonly, ana_pos_check=ana_pos_check)
    printinfo('Finished')
    lmsg = 'optic_reference Pfertig'
    return True


printinfo('try optic_reference(ele)')
