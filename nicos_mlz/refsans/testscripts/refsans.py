# pylint: skip-file

# import ++
from nicos import session
from numpy import array
import time
import threading
# import --

printinfo('tools 4 nicos MP 2023-10-12 08:03:20')

printinfo('todo read(0) pollinterval optic')

# tools ++
time_units = [
    [.001, 'ms'],
    [1, 'sec'],
    [60, 'min'],
    [60*60, 'houer'],
    [24*60*60, 'day'],
]


def avg_read(Elemente, anz, pause, style='val', param=None, verbose=True):
    """
    style:
    val = nur der mean
    std = liste [mean, std]
    debug = liste [mean, std, dif, min, max]
    """
    Debug = True
    res = []
    if param is None:
        param = 'read'
    for ii in range(len(Elemente)):
        res.append([])
    printinfo(f'avg_read from #nicos {anz:d}x{pause:.4f}sec={anz * pause:.4f}sec {len(Elemente):.4f}Elemente style {style:s}')
    if verbose:
        for ele in Elemente:
            printinfo(ele.name)
    tt = time.time()
    for i in range(anz):
        for ii in range(len(Elemente)):
            if param == 'read':
                res[ii].append(Elemente[ii].read(0))
            else:
                res[ii].append(getattr(Elemente[ii], param))
        line = ''
        if len(Elemente) == 1:
            line = " {0:.4f}".format(res[ii][-1])
            if len(res[ii]) >= 2:
                line += " dif: {0:.4f}".format(res[ii][-1] - res[ii][-2])
        if verbose:
            printinfo("{0:d}/{1:d}".format(i, anz) + line)
        sleep(pause)   # kein tread
    if verbose:
        printinfo(f'avg_read from #nicos {anz:d}x{pause:.4f}sec={anz * pause:.4f}sec {len(Elemente):.4f}Elemente style {style:s}')
    printinfo(f'in {time.time() - tt:.2f} sec')
    for i, elem in enumerate(Elemente):
        res[i] = array(res[i])
        mean = res[i].mean()
        std = res[i].std()
        mm = min(res[i])
        xx = max(res[i])
        printinfo(f'{i:d}: {elem.name:s} {mean:.5f} +/- {std:.5f}')
        if style == 'val':
            res[i] = mean
        elif style == 'std':
            res[i] = [mean, std]
        elif style == 'debug':
            res[i] = [mean, std, xx - mm, mm, xx]
        else:
            printinfo('unknown style', style)
            res[i] = mean
    return res


class cl_zweig(threading.Thread):
    '''A thread class describing an instrument used to measure time averaged
    signals from a data source '''
    dataLock = threading.Lock()
    id = 0

    def __init__(self, name, Order, method, argument, Debug=False, readonly=False):
        self.__Debug = Debug
        self.__readonly = readonly
        threading.Thread.__init__(self)
        self.id = cl_zweig.id
        # Each new instument gets a name and is connected to a data source
        cl_zweig.id += 1
        if name == 'thread':
            method = 'all'
        self.name = name
        self.Order = Order
        self.method = method
        self.argument = argument
        return

    def run(self):
        '''Overrides the thread start() method and defines the behaviour of the thread instrument'''
        Debug = self.__Debug  # and False
        self.result = {}
        if Debug:
            line = f'Debugging run name {self.name} type {type(self.name)}' \
                   f'Order {self.Order} method {self.method} argument {self.argument}' \
                   f'type {type(self.argument)}'
            printinfo(line)
        if self.Order == 'method':
            if self.argument is None:
                try:
                    if self.__readonly:
                        self.result[self.name] = 'BLOCKED'
                    else:
                        self.result[self.name] = getattr(session.devices[self.name], self.method)()  # None
                except:
                    self.result[self.name] = str(sys.exc_info()[0])
            else:
                try:
                    if self.__readonly:
                        self.result[self.name] = 'BLOCKED'
                    else:
                        self.result[self.name] = getattr(session.devices[self.name], self.method)(self.argument)
                except:
                    self.result[self.name] = str(sys.exc_info()[0])
#         elif    self.Order == 'class':
#                 if self.argument is None:
#                     try:
#                         self.result[self.name] = getattr(classe,self.method)(self.name)
#                     except:
#                         self.result[self.name] = str(sys.exc_info()[0])
#                 else:
#                     try:
#                         self.result[self.name] = getattr(classe,self.method)(self.name, self.argument)
#                     except:
#                         self.result[self.name] = str(sys.exc_info()[0]) + 'TAG!'
        elif self.Order == 'func':
            try:
                if self.__readonly:
                    self.result[self.name] = 'BLOCKED'
                else:
                    self.result[self.name] = self.method(self.argument)
            except:
                self.result[self.name] = 'EXCEPT '+str(sys.exc_info()[0])
        else:
            printinfo('Oder: >', self.Order, '< with arg: >', self.argument, '<')
            raise NicosError('ill order')


class cl_D4A():
    """this class does all the work with the threads
    only one var of cl_D4A
    """

    def __init__(self, Debug=False, readonly=False):
        self.__Debug = Debug
        self.__readonly = readonly

    def info(self):
        line = 'info of cl_D4A '
        line += 'D4A '
        line += 'Debug %s ' % str(self.__Debug)
        line += 'readonly %s ' % str(self.__readonly)
        printinfo(line)

    def loop(self, li_readers, arg):
        arg += 1
        try:
            for reader in li_readers:
                reader.join()
        except:
            self.loop(li_readers, arg)

    def execute(self, parts=None, Order='Oinit', method='Minit', argument='Ainit'):
        """runns the threads"""
        Debug = self.__Debug  # and False
        readonly = self.__readonly
        running_source_threads = []
        if Debug:
            line = 'read0 _execute'
            line += 'P: %s ' % str(parts)
            line += 'type(parts) %s ' % str(type(parts))
            line += 'O: %s ' % str(Order)
            line += 'M: %s ' % str(method)
            line += 'type(argument) %s ' % str(type(argument))
            printinfo(line)
        # Idem for the instruments
        li_readers = []
        keep = {}
        # if 'thread' not in argument.keys():
        #     argument['thread'] = None

        for Element in argument:
            if Debug:
                line = ''
                line += 'creating Element:'+str(Element)
                line += ' for: O:' + str(Order)
                line += ' M:' + str(method)
                line += ' A:' + str(Element)
                printinfo(line)
            li_readers.append(cl_zweig(Element, Order, method, Element, Debug, readonly))
            if Debug:
                printinfo('i am the reader: %s <' % (li_readers[-1]))
        # for the fun I started them separately... not so fun after all
        if Debug:
            printinfo(li_readers)
        for r in li_readers:
            r.start()
        # !!!! Importantissimissimo!!!! Here we wait for all the readeDr threads to have finished their job
        self.loop(li_readers, 0)
        if Debug:
            printinfo('End of Loop')
        # Once they are done we can look at their result
        for thread in li_readers:
            keep.update(thread.result)
            if Debug:
                line = ''
                line += 'thread '
                line += '%s ' % str(thread)
                line += 'id%s ' % thread.id
                # line += '%s' % thread._Thread__name
                line += 'name = %s ' % thread.name
                line += 'result >%s< ' % thread.result
                printinfo(line)
        # a = raw_input('hit Return to exit')
        # Up to now that is the only way I have found... maybe not the best
        for el in running_source_threads:
            el._Thread__stop()  # = True
        return keep

# tools --


# function ++
def chopper_full_state(
        verbose=False,
        ):
    res = True
    lines = []
    warning = []
    missing = []
    try:
        delphin_res = {}
        for sele in [
                                'chopper_expertvibro',
                                'chopper_no_Warning',
                                'chopper_vibration_ok',
                                'ChopperEnable1',
                                ]:
            ele = session.devices[sele]
            condition = ele.read(0)
            delphin_res[ele.name] = condition
            if ele.name != 'chopper_expertvibro':  # maybe Manual ON
                res = res and (condition == 'On')
            lines.append('%20s:   %s %s' % (ele.name, condition, ele.status(0)[1]))
        if 'off' == delphin_res['chopper_expertvibro'].lower() and\
           'on' == delphin_res['chopper_vibration_ok'].lower():
            printwarning('expertvibro8 in Manual ON')
    except:
        res = False
        missing.append('vsd')

    try:
        fatal = chopper.fatal
        res = res and (fatal == 'ok')
        lines.append('%14s fatal    %s %s' % (chopper.name, fatal, chopper.status(0)[1]))

        aktchopper2 = chopper2_pos.read(0)
        statchopper2 = chopper2_pos.status(0)[1]
        if statchopper2 == '':
            statchopper2 = 'ok'
        elif statchopper2 == 'device not referenced':
            res = False
        else:
            lines.append('running chopper2_pos')
            res = False
        line = 'deep '
        line += 'Y %12d ' % session.devices['chopper2_pos_y'].read(0)
        line += 'X %12d ' % session.devices['chopper2_pos_x'].read(0)
        lines.append(line)
        lines.append('%14s          %d %s' % (chopper2_pos.name, aktchopper2, statchopper2))
        res = res and not (aktchopper2 == 0)

        speed = []
        status = []
        for sele in ['chopper_speed', 'chopper2', 'chopper3', 'chopper4', 'chopper5', 'chopper6']:
            ele = session.devices[sele]
            condition = ele.condition
            res = res and (condition == 'ok')
            lspeed = ele.read(0)
            gear = ele.gear
            lstatus = ele.status(0)[1]
            lines.append('%14s %8s %s %s %d' % (ele.name, lstatus, lspeed, condition, gear))
            if gear == 0:
                gear = 1  # chopper_speed
            speed.append(lspeed * gear)
            status.append(lstatus)
        if 'speed' in status[1:]:
            lines.append(status)
            lines.append('async')
            res = False
        elif 'position' in status[1:]:
            lines.append(status)
            lines.append('async mode')
            res = False
        elif 'break' in status:
            lines.append('break')

        mix = max(speed) - min(speed)
        if mix > 2:
            lines.append('async speed %f > 2' % mix)
            res = False
    except:
        res = False
        missing.append('chopper')

    try:
        lines.append('expertvibro8')
        for i in range(4):
            line = ''
            index = i + 1
            line += '%d: ' % index
            ele = session.devices['expertvibro8_Amplitude_%d' % index].read(0)
            line += 'A: %.2f ' % ele
            ele = session.devices['expertvibro8_Frequenz_%d' % index].read(0)
            line += 'F: %.2f ' % ele
            lines.append(line)
    except:
        res = False
        missing.append('expertvibro8')

    try:
        ele = cpt00
        val = ele.read(0)
        lines.append('%14s %8s %f' % (ele.name, ele.status(0)[1], val))
        if min(speed) > 1:
            lines.append('running')
            if abs(val) > 1:
                res = False
        else:
            warning.append('as STOP check cpt00 only running')
    except:
        res = False
        missing.append('chopperphasentiming')

    try:
        lines.append('shutter: %s' % shutter.read(0))
    except:
        res = False
        missing.append('shutter')

    try:
        val = 0
        for sub in ['CB', 'SFK']:
            ele = session.devices['chamber_' + sub]
            lval = ele.read(0)
            lines.append('%20s:   %f %s' % (ele.name, lval, ele.status(0)[1]))
            val = max(val, lval)
        if val > 10:
            warning.append('running in Air %f' % val)
    except:
        res = False
        missing.append('chamber')

    if verbose or not res:
        for line in lines:
            printinfo(line)
    if len(warning) > 0:
        printinfo('warnings:')
        for line in warning:
            printinfo('! ' + line)
    if len(missing) > 0:
        line = 'missing setups:\n'
        for l in missing:
            line += "AddSetup('%s')\n" % l
        printinfo(line)
    return res


def chopper_reference(
    disc2_pos=1,
    speed=500,
    final=234.09,  # 2023-04-06 14:13:35 done mit MH
    delay_automatic=True,  # and False    #auch unjustiert!
    verbose=True,
   ):

    from nicos import session

    StrElemente1 = [
        'chopper_speed',
        'chopper2',
        'chopper3',
        'chopper4',
        'chopper5',
        'chopper6',
        'cptoptic1',
        'cptoptic2',
        'cptoptic3',
        'cptoptic4',
            ]
    StrElemente2 = [
        'cpt00',
        'cpt01',
        'cpt1',
        'cpt2',
        'cpt3',
        'cpt4',
        'cpt5',
        'cpt6',
        'chopper1_temp',
        'chopper2_temp',
        'chopper3_temp',
        'chopper4_temp',
        'chopper5_temp',
        'chopper6_temp',
        'expertvibro8_Phase_1',
        'expertvibro8_Phase_2',
        'expertvibro8_Phase_3',
        'expertvibro8_Phase_4',
        'expertvibro8_trigger_1',
        'expertvibro8_trigger_2',
        'expertvibro8_trigger_3',
        'expertvibro8_trigger_4',
        'expertvibro8_Amplitude_1',
        'expertvibro8_Amplitude_2',
        'expertvibro8_Amplitude_3',
        'expertvibro8_Amplitude_4',
        # 'expertvibro8_Frequenz_1',
        # 'expertvibro8_Frequenz_2',
        # 'expertvibro8_Frequenz_3',
        # 'expertvibro8_Frequenz_4',
        'Temperature1',
        'Temperature2',
        'chamber_CB',
        'chamber_SFK',
        'Water1Flow',
        'Water1Temp',
        'Water2Flow',
        'Water2Temp',
        ]

    def chopper_deep_XY_line():
        line = ''
        line += 'Y %12d ' % session.devices['chopper2_pos_y'].read(0)
        line += 'X %12d ' % session.devices['chopper2_pos_x'].read(0)
        return line

    def chopper2_pos_maw(pos=None):
        menachem = time.time()
        if pos is None:
            printinfo('chopper2_pos_maw wait')
        else:
            printinfo('chopper2_pos_maw %d' % pos)
            chopper2_pos.move(pos)
        sleep(1)
        while True:
            line = chopper_deep_XY_line()
            std = chopper2_pos.status(0)
            line += '%d %s ' % (std[0], std[1])
            line += str(std[0] == 200)
            printinfo(line)
            if std[0] == 200:
                dauer = (time.time() - menachem) / 60
                printinfo('time %.2fmin' % dauer)
                break
            sleep(.9)
        sleep(1)
        return 'ok'

    def commute_fine(self=chopper, verbose=verbose):
        Elemente2 = [
                expertvibro8_Amplitude_1,
                expertvibro8_Amplitude_2,
                expertvibro8_Amplitude_3,
                expertvibro8_Amplitude_4,
                ]
        menachem = time.time()
        glob_con = []
        printinfo(chopper_deep_XY_line())
        printinfo(chopper.fatal)
        printinfo('shut_down just wait')
        if ChopperEnable1.read(0) != 'On' or chopper_no_Warning.read(0) != 'On':
            expertvibro8_Amplitude_1.reset()
            tt = time.time() + 2 * 45
            while True:
                if ChopperEnable1.read(0) == 'On':
                    break
                if time.time() > tt:
                    return 'Delphin pwr ON timeout'
                sleep(5)
        chopper._shut_down()
        sleep(1)
        lmsg = self.fatal
        if lmsg != 'ok':
            return 'fatal: ' + lmsg
        printinfo(chopper_deep_XY_line())
        chopper.delay = 0
        sleep(1)
        # chopper._attached_comm.writeLine('m5000=31') #63
        # printwarning('no disc6!')
        chopper._commute()
        printinfo('chopper.delay', chopper.delay)
        printinfo(chopper_deep_XY_line())
        while True:
            ele = chopper
            ready = True
            line = ''
            line += '%14s ' % ele.name
            line += '%s ' % ele.fatal
            std = ele.status(0)[1]
            line += '%s ' % std
            if std not in ['moving', 'speed', 'inactive']:
                ready = False
            printinfo(line)
            for ele in [
                    self._attached_chopper1,
                    self._attached_chopper2,
                    self._attached_chopper3,
                    self._attached_chopper4,
                    self._attached_chopper5,
                    self._attached_chopper6,
                    ]:  # Elemente:
                line = ''
                line += '%14s ' % ele.name
                line += '%7.2f ' % ele.phase
                cond = ele.condition
                line += '%s ' % cond
                std = ele.status(0)[1]
                line += '%s ' % std
                if std not in ['moving', 'speed', 'inactive']:
                    ready = False
                if cond not in glob_con:
                    glob_con.append(cond)
                printinfo(line)
            line = 'Vib'
            for ele in Elemente2:
                line += '%5.1f' % ele.read(0)
            printinfo(line)
            dauer = (time.time() - menachem) / 60
            printinfo('time %.2fmin' % dauer)
            if dauer > 30:
                return 'timeout > 30sec'
            if ready:
                if verbose:
                    printinfo('chopper_reference chopper2_pos_maw(1)')
                res = chopper2_pos_maw(1)
                printinfo(chopper_deep_XY_line())
                if res != 'ok':
                    return res
                chopper._set_all_phases()
                printinfo('READY')
                return 'ok'
            for test in glob_con:
                for tag in ['Fatal Following Error']:
                    if tag in test:
                        printinfo(tag)
                        return tag
            sleep(.9)
        return 'commute_fine functionsende'

    def set_delay_proof(pp, iter=3, schlafen=2.25,
                        cptElemente=[
                            cpt00, cpt01, cpt2, cpt3, cpt4, cpt5, cpt6,
                            cptoptic1,
                            cptoptic2,
                            cptoptic3,
                            cptoptic4,
                        ]
                        ):
        chopper.delay = pp
        sleep(1)
        avg_read(cptElemente, iter, pause=1)
        sleep(schlafen)
        avg_read(cptElemente, iter, pause=1)
        sleep(schlafen)
        avg_read(cptElemente, iter, pause=1)

    def start_test(iter=3, Liste=list(range(0, 361, 10)), schlafen=2.25, check=None, val=180):
        """
        iter=3, Liste=list(range(0,361,10)), schlafen=22.5
        """
        for pp in [0] + Liste + [0]:
            printinfo('start_test {0:d}'.format(pp))
            try:
                set_delay_proof(pp, iter, schlafen)
            except:
                # lesefehler speed div null
                set_delay_proof(pp, iter, schlafen)
            if check is not None:
                akt = check.read(0)
                if akt <= val:
                    # Abbruch
                    return True
        printinfo('Pfertig')
        return False

    def set_delay_automatic(final=final):
        Notausgang = 5
        anz = 1
        while anz <= Notausgang:
            if start_test(iter=anz, schlafen=.5, check=cpt00):
                set_delay_proof(final, iter=1, schlafen=.5)
                return anz
            anz += 1
        printerror('set_delay_automatic FAIL')
        1/0

    def chopper_pollinerval_set(StrElemente):
        pi = 5
        for tag in StrElemente:
            set(tag, 'pollinterval', pi)
            pi += .1

    def chopper_pollinerval_clear(StrElemente1, StrElemente2):
        for tag in StrElemente1:
            set(tag, 'pollinterval', None)
        for tag in StrElemente2:
            set(tag, 'pollinterval', 500)

    def printremark(style, line):
        if style == 'info':
            printinfo(line)
        elif style == 'error':
            printerror(line)
        elif style == 'warning':
            printwarning(line)
        else:
            line = '%s' % style.upper() + line
            printerror(line)
        Remark(line)
        return line

    self = chopper
    lmsg = self.fatal
    if lmsg not in ['ok',
                    'No commutation',
                    'E-stop backplane: ChopperLogic',
                    'No commutation, E-stop backplane: ChopperLogic',
                    'E-stop Frontswitch',
                    ]:
        return printremark('error', 'Primcheck ' + lmsg)
    if disc2_pos > 5:
        return printremark('error', 'disc2_pos > 5 use real pos only not {0:d}'.format(disc2_pos))
    chopper_pollinerval_set(StrElemente1 + StrElemente2)
    printremark('info', 'chopper referencing running:' + lmsg)
    printinfo('chopper_reference break')
    try:
        waiting = []
        for ele in [
            self._attached_chopper1,
            self._attached_chopper2,
            self._attached_chopper3,
            self._attached_chopper4,
            self._attached_chopper5,
            self._attached_chopper6,
           ]:
            if ele.mode == 4:
                ele.move(0)
                waiting.append(ele)
        if len(waiting) > 0:
            wait(*waiting)
        else:
            printinfo('chopper_reference no wait')
            1/0  # to be sure!
    except:
        printinfo('EXCEPT chopper_speed.maw(0)')
        while True:
            sleep(10)
            akt = [ele.read(0) for ele in [
                self._attached_chopper1,
                self._attached_chopper2,
                self._attached_chopper3,
                self._attached_chopper4,
                self._attached_chopper5,
                self._attached_chopper6,
                ]]
            printinfo(akt,'manual wait for speed')
            if max(akt) < 2:
                break
    res = commute_fine(self, verbose=verbose)
    if res == 'ok':
        if disc2_pos != 1:
            if verbose:
                printinfo('chopper_reference final disc2_pos %d' % disc2_pos)
            chopper2_pos_maw(disc2_pos)
        if delay_automatic:
            printinfo('chopper_reference accelerate')
            chopper_speed.maw(speed)
            printinfo('chopper_reference set_delay_automatic')
            lmsg = 'chopper_reference done! with %d' % set_delay_automatic(final=final)
        else:
            lmsg = 'NO delay_automatic: chopper_reference done!'
    else:
        chopper_pollinerval_clear(StrElemente1, StrElemente2)
        printremark('error', 'chopper reference error: kill the script')
        1/0
    chopper_pollinerval_clear(StrElemente1, StrElemente2)
    printremark('info', lmsg)
    return True


# function --
Remark('REFSANS greets his friends')
