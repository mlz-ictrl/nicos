description = 'PANDA Heusler-monochromator'

group = 'lowlevel'

includes = []

modules = []

excludes = ['mono_pg', 'mono_cu', 'mono_si']

extended = dict( dynamic_loaded = True)

# for ipc-stuff
MOTOR = lambda x: 0x50 + x
devices = dict(
    mono_heusler     = device('devices.tas.Monochromator',
                              description = 'PANDA Heusler monochromator',
                              unit = 'A-1',
                              theta = 'mth',
                              twotheta = 'mtt',
                              reltheta = True,
                              focush = None,
                              focusv = 'mfv_heusler',
                              hfocuspars = [0],
                              vfocuspars = [-214.235, 62.1267, -6.12963],
                              abslimits = (1, 10),
                              dvalue = 3.45,
                              scatteringsense = -1,
                              fixed = 'Please give me correct parameters first !',
                              fixedby = ('brain', 99),
                             ),
    mfv_heusler_step = device('panda.mcc2.MCC2Motor',
                              description = 'vertical focusing MOTOR of Heusler monochromator',
                              bus = 'focimotorbus',
                              mccmovement = 'linear',
                              precision = 0.01,
                              fmtstr = '%.3f',
                              channel = 'X',
                              addr = 0,
                              slope = 400 * 8 / 360.,
                              abslimits = (-360, 360),
                              userlimits = (-4, 340),
                              unit = 'deg',
                              idlecurrent = 0.4,
                              movecurrent = 1.2,
                              rampcurrent = 1.3,
                              microstep = 8,
                              speed = 5,
                              accel = 5,
                              lowlevel = True,
                              fixed = 'Please give me correct parameters first !',
                              fixedby = ('brain', 99),
                             ),
    mfv_heusler_poti = device('panda.mcc2.MCC2Poti',
                              description = 'vertical focusing CODER of Heusler monochromator',
                              bus = 'focimotorbus',
                              fmtstr = '%.3f',
                              channel = 'X',
                              addr = 0,
                              slope = 1024.0 / 5.0, #???
                              unit = 'mm',
                              zerosteps = 0,
                              lowlevel = True,
                             ),
    mfv_heusler      = device('panda.rot_axis.RotAxis',
                              description = 'vertical focus of Heusler monochromator',
                              motor = 'mfv_heusler_step',
                              coder = 'mfv_heusler_step',
                              obs = ['mfv_heusler_poti'],
                              precision = 0.01,
                              backlash = 0,
                              refpos = 306,
                              lowlevel = True,
                              fixed = 'Please give me correct parameters first !',
                              fixedby = ('brain', 99),
                             ),
    ana_heusler      = device('devices.tas.Monochromator',
                              description = 'PANDA\'s Heusler ana',
                              unit = 'A-1',
                              theta = 'ath',
                              twotheta = 'att',
                              focush = 'afh_heusler',
                              focusv = None,
                              abslimits = (1, 10),
                              hfocuspars = [44.8615, 4.64632, 2.22023],
                              dvalue = 3.45,
                              scatteringsense = -1,
                             ),
    afh_heu_step = device('devices.vendor.ipc.Motor',
                          description = 'stepper for horizontal focus of heusler ana',
                          bus = 'bus1',
                          addr = MOTOR(8),
                          slope = 8 * 400 / 360.0,
                          unit = 'deg',
                          abslimits = (-179, 179),
                          zerosteps = 500000,
                          speed = 20,
                          accel = 15,
                          microstep = 2 * 8,
                          startdelay = 0,
                          stopdelay = 0,
                          ramptype = 1,
                          lowlevel = True,
                         ),
    afh_heu      = device('panda.rot_axis.RotAxis',
                          description = 'horizontal focus of heusler ana',
                          motor = 'afh_heu_step',
                          coder = 'afh_heu_step',
                          dragerror = 5,
                          abslimits = (-179, 179),
                          obs = [],
                          precision = 1,
                          fmtstr = '%.1f',
                          autoref = None, # disable autoref since there is no refswitch
                         ),
)

startupcode = """
try:
    _=(ana, mono, mfv, mfh, focibox)
except NameError, e:
    printerror("The requested setup 'panda' is not fully loaded!")
    raise NameError('One of the required devices is not loaded : %s, please check!' % e)

if focibox.read(0) == 'Heusler':
    from nicos import session
    mfh.alias = None
    mfv.alias = session.getDevice('mfv_heusler')
    mono.alias = session.getDevice('mono_heusler')
    ana.alias = session.getDevice('ana_heu')
    #mfh.motor._pushParams() # forcibly send parameters to HW
    mfv.motor._pushParams() # forcibly send parameters to HW
    #focibox.comm('XME',forcechannel=False) # enable output for mfh
    focibox.comm('YME',forcechannel=False) # enable output for mfv
    focibox.driverenable = True
    maw(mtx, 0) #correct center of rotation for Si-mono only
    del session
else:
    printerror('WRONG MONO ON TABLE FOR SETUP mono_heusler !!!')
"""