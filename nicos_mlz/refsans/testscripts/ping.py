# pylint: skip-file

# test: subdirs = frm2
# test: setups = 07_refsans_full
# test: skip

"""
127.0.0.1
fritz.box
google.de
hektor.admin.frm2
jcnsps.jcns.frm2
minos.admin.frm2

"""
## userinterface ++
verbose = True and False
Geduld = 1  #tries of ping (to wake VPN, but not needed)

# group = 'ZE'
# group = 'home'
# group = 'start SE'
# group = 'devel'
# group = 'core'
group = 'restart'
# group = 'all'

## userinterface --

Debug = True and False
LDeveloping = True and False
readonly = False
home = '.refsans.frm2'
import threading
import os
import time

print('ping pong')
"""
                                                                                     a_Off     kann nicht abgeschaltet werden  SHS, Janiza
                                                                                     b_core    wird auch ohne n gebraucht      server, hub, raid, BigBrain, refsanswin, VSD, USV, refsansuser
                                                                                     c_low     optimaler Start nach Pause      Pumpstand for Vakuum aber kein NICOS
                                                                                     d_nicos   PCs, aber es geht noch nichts!  ctrl, hw
                                                                                     e_netze   Kommunikation                   Moxa Hubs
                                                                                     f_setup   die devices von NICOS           shutter, chopper, ...
                                                                                     g_option  nur in bestimmten setups        polarisator
                                                                                     h_se      SampleEnvironmend               julabo,
                                                                                     i_human   devices only vor human          screens, Loetkolben, Licht   Schaltbar
                                                                                     j_devel   Development                     refsansdevel, beckhoffgate
                                                                                     k_spare   Ersatzgeraete                   refsansctrl02, refsans023
                                                                                     l_extern  externe sachen                  toftof, zeiterfassung
                                                                                     m_extra   sonstiges                       neue Gruppe?
    #['URL',                        '#kommentar',                                   'a_Off',    'ord01'],
"""
mandatory = [
    ['syringe01',                   'SE developing',                                'h_se',     'ord41'],
    ['bigbrain',                    'bigbrian next to Rack5',                       'b_core',   'ord09'],
    ['detector',                    'alias',                                        'f_setup',  'ord10'],
    ['detector01',                  'EZ 2022-09-20 13:58:55',                       'f_setup',  'ord10'],
    ['refsansctrl',                 'Rack5 alias',                                  'b_core',   'ord12'],
    ['refsansctrl01',               'Rack5 Pizzabox',                               'b_core',   'ord13'],
    ['refsanshw',                   'Rack5 alias',                                  'b_core',   'ord16'],
    ['refsanshw01',                 'Rack5 Pizzabox',                               'b_core',   'ord17'],
    ['refsanssci1',                 'win-PC nutzer am PO',                          'f_setup',  'ord19'],
    ['refsanssrv',                  'der Server',                                   'b_core',   'ord20'],
    ['refsansuser',                 'Nutzer PC Linux cabine',                       'b_core',   'ord22'],
    ['refsanswin',                  'win-PC Rack1',                                 'b_core',   'ord23'],
    ['ana4gpio01',                  'B3; gonio_x + julabo_flow + humidity',         'f_setup',  'ord24'],
    ['ana4gpio02',                  'yoke; yoke_xy + humidity',                     'f_setup',  'ord25'],
    ['ddgana4',                     'Rack4; D900_h3 + nc + humidity',               'f_setup',  'ord26'],
    ['beckhoff-1',                  'EZ 2022-09-20 14:01:10',                       'f_setup',  'ord28'],
    ['camera',                      'Camera at PO',                                 'a_Off',    'ord29'],
    ['janitza',                     'janitza at Unterverteilung',                   'a_Off',    'ord29'],
    ['cpt',                         'EZ 2022-11-14 14:02:42',                       'f_setup',  'ord30'],
    ['detektorantrieb',             'EZ 2022-09-20 14:01:10',                       'f_setup',  'ord31'],
    ['expertvibro8',                'EZ 2022-11-14 14:02:42',                       'f_setup',  'ord32'],
    ['gonio1',                      'rep 2024-01-24 15:26:51',                      'f_setup',  'ord33'],
    ['gonio2',                      'EZ 2022-09-20 14:01:10',                       'f_setup',  'ord34'],
    ['gonio3',                      'EZ 2022-09-20 14:01:10',                       'f_setup',  'ord35'],
    ['hw',                          'alias',                                        'b_core',   'ord36'],
    ['ctrl',                        'alias',                                        'b_core',   'ord37'],
    ['user',                        'alias',                                        'b_core',   'ord38'],
    # ['heater01',                    'SE schrank',                                   'h_se',     'ord41'],
    ['horizontalblende',            'EZ 2022-09-20 14:01:10',                       'f_setup',  'ord42'],
    # ['julabo01',                    'EZ 2022-09-01 08:31:53',                       'h_se',     'ord43'],
    ['monitor01',                   'EZ 2022-09-20 14:02:59 Kabine',                'i_human',  'ord46'],
    ['monitor02',                   'EZ 2022-09-20 14:02:59 Kabine',                'i_human',  'ord47'],
    ['monitor03',                   'EZ 2022-09-20 14:02:59 Kabine',                'i_human',  'ord48'],
    ['monitor04',                   'EZ 2022-09-20 14:02:59 Kabine',                'i_human',  'ord49'],
    ['monitor05',                   'EZ 2022-09-20 14:02:59 Terrase',               'i_human',  'ord50'],
    # ['monitor11',                   'reuse 2023-09-14 07:54:46 humidity01',     'k_spare',  'ord51'],
    ['humidity01',                  '2023-09-14 07:55:05',                              'f_setup', 'ord00'],
    # ['monitor12',                   'der ist vermisst',                             'm_extra',  'ord52'],
    # ['monitor13',                   'ana4gpio03 change 2023-05-02 10:52:15',        'k_spare',  'ord53'],
    ['raspicampo',                  'EZ 2022-09-20 14:02:59 Kabine',                'i_human',  'ord55'],
    # ['hplc',                        'SE HPLC-Pumpe',                                'h_se',     'ord57'],
    # ['valvein',                     'SE HPLC-Pumpe Ventil',                         'h_se',     'ord58'],
    # ['valveout',                    'SE HPLC-Pumpe Ventil',                         'h_se',     'ord59'],
    ['nimaservice',                 'Filmwaage raspi',                              'h_se',     'ord61'],
    ['nimaana4',                    'Filmwaage Sensors',                            'h_se',     'ord61'],
    ['rs232-7',                     'Filmwaage',                                    'h_se',     'ord62'],
    ['optic',                       'EZ 2022-09-20 14:02:59',                       'f_setup',  'ord64'],
    ['pilz',                        '#kommentar',                                   'a_Off',    'ord66'],
    ['probenort',                   'b3h3 monitor EZ 2022-09-20 14:02:59',          'f_setup',  'ord68'],
    ['pumpenstand',                 'EZ 2024-01-24 15:26:12',                       'c_low',    'ord69'],
    ['rs232-2',                     'Moxa Rack1 rear',                              'e_netze',  'ord71'],
    ['rs232-3',                     'Moxa Rack1 rear',                              'e_netze',  'ord72'],
    ['rs232-5',                     'Moxa Medienversorgung',                        'e_netze',  'ord75'],
    ['savedetector',                'EZ 2022-09-20 14:02:59',                       'f_setup',  'ord78'],
    ['vsd',                         'VSD in Rack1',                                 'a_Off',    'ord86'],
    # ['TDVM3',                      'schrank',                                      'j_devel',  'ord89'],
    # ['TDVM4',                      'schrank',                                      'j_devel',  'ord90'],
    ['beckhoffgate',                '#kommentar',                                   'j_devel',  'ord08'],
    ['detector02',                  'EZ spare',                                     'k_spare',  'ord11'],
    ['refsansctrl02',               'EZ 2022-11-09 15:23:32',                       'k_spare',  'ord14'],
    ['refsansdevel',                'EZ 2022-11-09 15:23:08',                       'j_devel',  'ord15'],
    # ['refsans023',                  'EZ 2022-06-30 15:26:24',                       'j_devel',  'ord18'],
    ['antrax01',                    'EZ 2022-09-20 14:01:10',                       'j_devel',  'ord26'],
    # ['monitor41',                   'ist im Schrank',                               'm_extra',  'ord44'],
    # ['raspipyctor',                 'offline devel GM',                             'j_devel',  'ord45'],
    ['raspicam02',                  'Racks',                                        'j_devel',  'ord54'],
    # ['oszi1',                       'schrank kommentar',                            'j_devel',  'ord65'],
    # ['poe',                         'tool schrank',                                 'j_devel',  'ord67'],
    # ['raspi01',                     'schrank kommentar',                            'j_devel',  'ord70'],
    ['rs232-8',                     'Moxa Rack4 SR messelektronik',                  'e_netze',  'ord74'],
    # ['rs232-4',                     'Halle spare',                                   'e_netze',  'ord74'],
    # ['rzcp0367',                    'Terrasse',                                     'j_devel',  'ord77'],
    # ['wave1',                       'Schrank',                                      'j_devel',  'ord87'],
    # ['wave2',                       'Schrank',                                      'j_devel',  'ord88'],
    # ['172.25.18.254',               '#kommentar',                                   'l_extern', 'ord02'],
    # ['172.25.46.241',              'UYL 04 24 Regal',                              'l_extern', 'ord03'],
    # ['172.25.46.242',               'Zeiterfassung',                                'l_extern', 'ord04'],
    # ['172.25.46.243',               'Zeiterfassung',                                'l_extern', 'ord05'],
    # ['172.25.46.254',               'Zeiterfassung',                                'l_extern', 'ord06'],
    # ['172.25.99.254',               '#kommentar',                                   'l_extern', 'ord07'],
    # ['toftofsrv.toftof.frm2',       '#kommentar',                                   'l_extern', 'ord21'],
    ['height',                      'EZ 2022-09-20 14:02:59',                       'g_option', 'ord27'],
    # ['guidefield',                  'machen aus nicos alt!',                        'g_option', 'ord39'],
    # ['guidefield2',                 'wie guidefield',                               'g_option', 'ord40'],
    ['memograph07.care.frm2',       'ist borstig, we accept that',                  'l_extern', 'ord73'],
    # ['rs232-6',                    'Nesly Aslan hochdruckzelle',                    'l_extern', 'ord76'],
    ['smtp.frm2.tum.de',            '#kommentar',                                   'l_extern', 'ord79'],
    ['sw-refsans.admin.frm2',       '#kommentar',                                   'l_extern', 'ord80'],
    ['erebos.frm2.tum.de',          '#kommentar',                                   'l_extern', 'ord81'],
    ['moros.frm2.tum.de',           '#kommentar',                                   'l_extern', 'ord82'],
    # ['raidng-refsans.admin.frm2',   'pingt nur in admin und vpn',                   'l_extern', 'ord83'],
    # ['terminalserver.hereon.de',   'pingt nicht trotz RDP Verbingung 25.03.2021',  'l_extern', 'ord84'],
    # ['141.4.40.203',               'die IP des terminalserver geht nicht ',        'l_extern', 'ord85'],
    ]


def ping(arg, Geduld=Geduld, group=group, Debug=Debug):
    if Debug:
        printinfo('ping : >%s<' % str(arg))
    history = []
    res = 'cry'
    extra_msg = False
    from_arg = False

    if type(arg) == type(''):
        arg = [arg, 'no response', 'arg', 'ordxx']
        from_arg = True

    URL = arg[0]
    if URL[0] == '#':
        if group == 'all':
            URL = URL[1:]
        else:
            return arg[0] + ': ' + arg[1]
    text = ' info: ' + arg[1]
    full = URL
    if '.' not in full:
        full += home
    Geduld_use = Geduld
    while Geduld_use:
        ot = os.system('ping '+full+' -c 1')
        if ot == 0:
           res = ''
           break
        elif ot == 512:
           res = 'unknown host'
           break
        elif ot == 256:
            res = ''  # Destination Host Unreachable'
        else:
            res = 'cry unknown result von ping >%s<'%str(ot)
            break
        if Debug:
            print ('%d %s' % (Geduld_use,res))
        if res not in history:
            history.append(res)
        Geduld_use -= 1
        if not Geduld_use:
            res = URL + ': ' + res + text
            break
        printinfo('%s: %s' % (full, res))
        #sleep(1)
        extra_msg = True
        if extra_msg and res != True:
            if history != [] and False:
                res += ' extra_msg %s Geduld %d history %s'%(URL,Geduld_use,str(history))
        elif verbose:
            printinfo('%d %s' %((Geduld - Geduld_use + 1),URL))
        if from_arg:
            if res == '':
                res = 'ok'
        return res


tt = time.time()
D4A = cl_D4A()
if LDeveloping:
    res = D4A.execute(Order='func', method=ping,
                      argument=[
                        ['refsanssrv', 'der Server',             'b_core', 'ord20'],
                        ['bigbrain',   'bigbrain next to Rack5', 'b_core', 'ord09'], ])
else:
    res = D4A.execute(Order='func', method=ping, argument=mandatory)

Liste = []
for key in res.keys():
    if len(res[key]) == 0:
        pass
    else:
        if key not in res[key]:
            Liste.append(key + ' ' + res[key])
        else:
            Liste.append(res[key])
if len(Liste) > 0:
    Liste.sort()
    printinfo('please check in detail:')
    for line in Liste:
        printinfo(line)
printinfo('in %.1fsec' % ((time.time() - tt)))
printinfo('in %.1fmin' % ((time.time() - tt) / 60))
