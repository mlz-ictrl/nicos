description = 'PANDA Cu-monochromator'

group = 'lowlevel'

includes = ['monofoci', 'monoturm', 'panda_s7']

modules = []

excludes = ['mono_pg', 'mono_si', 'mono_heusler']

extended = dict(dynamic_loaded = True)

devices = dict(
    mono_cu     = device('devices.tas.Monochromator',
                         description = 'PANDA Cu monochromator',
                         unit = 'A-1',
                         theta = 'mth',
                         twotheta = 'mtt',
                         reltheta = True,
                         focush = 'mfh_cu',
                         focusv = 'mfv_cu',
                         hfocuspars = [0],
                         vfocuspars = [0],
                         abslimits = (1, 10),
                         dvalue = 3.455,
                         scatteringsense = -1,
                         crystalside = -1,
                         fixed = 'Please give me correct parameters first !',
                         fixedby = ('brain', 99),
                        ),
    mfh_cu_step = device('panda.mcc2.MCC2Motor',
                         description = 'horizontal focusing MOTOR of Cu monochromator',
                         bus = 'focimotorbus',
                         mccmovement = 'linear',
                         precision = 0.01,
                         fmtstr = '%.3f',
                         channel = 'X',
                         addr = 0,
                         slope = 27000. / 5,
                         abslimits = (1, 5),
                         userlimits = (1, 5),
                         unit = 'mm',
                         idlecurrent = 0.6,
                         movecurrent = 1.3,
                         rampcurrent = 1.3,
                         microstep = 8,
                         speed = 5.0 / 54.0,
                         accel = 5.0 / 54.0,
                         lowlevel = True,
                         fixed = 'Please give me correct parameters first !',
                         fixedby = ('brain', 99),
                        ),
    mfh_cu_poti = device('panda.mcc2.MCC2Poti',
                         description = 'horizontal focusing CODER of Cu monochromator',
                         bus = 'focimotorbus',
                         fmtstr = '%.3f',
                         channel = 'X',
                         addr = 0,
                         slope = 1024.0 / 5, #???
                         unit = 'mm',
                         zerosteps = 0,
                         lowlevel = True,
                        ),
    mfh_cu      = device('devices.generic.Axis',
                         description = 'horizontal focus of Cu monochromator',
                         motor = 'mfh_cu_step',
                         coder = 'mfh_cu_step',
                         obs = ['mfh_cu_poti'],
                         precision = 0.01,
                         backlash = 0,
                         lowlevel = True,
                         fixed = 'Please give me correct parameters first !',
                         fixedby = ('brain', 99),
                        ),
    mfv_cu_step = device('panda.mcc2.MCC2Motor',
                         description = 'vertical focusing MOTOR of Cu monochromator',
                         bus = 'focimotorbus',
                         mccmovement = 'linear',
                         precision = 0.01,
                         fmtstr = '%.3f',
                         channel = 'X',
                         addr = 0,
                         slope = 27000.0 / 5,
                         abslimits = (1, 5),
                         userlimits = (1, 5),
                         unit = 'mm',
                         idlecurrent = 0.6,
                         movecurrent = 1.3,
                         rampcurrent = 1.3,
                         microstep = 8,
                         speed = 5.0 / 54.0,
                         accel = 5.0 / 54.0,
                         lowlevel = True,
                         fixed = 'Please give me correct parameters first !',
                         fixedby = ('brain', 99),
                        ),
    mfv_cu_poti = device('panda.mcc2.MCC2Poti',
                         description = 'vertical focusing CODER of Cu monochromator',
                         bus = 'focimotorbus',
                         fmtstr = '%.3f',
                         channel = 'X',
                         addr = 0,
                         slope = 1024.0 / 5, #???
                         unit = 'mm',
                         zerosteps = 0,
                         lowlevel = True,
                        ),
    mfv_cu      = device('devices.generic.Axis',
                         description = 'vertical focus of Cu monochromator',
                         motor = 'mfv_cu_step',
                         coder = 'mfv_cu_step',
                         obs = ['mfv_cu_poti'],
                         precision = 0.01,
                         backlash = 0,
                         lowlevel = True,
                         fixed = 'Please give me correct parameters first !',
                         fixedby = ('brain', 99),
                        ),
)

startupcode = '''
try:
    _ = (ana, mono, mfv, mfh, focibox)
except NameError as e:
    printerror("The requested setup 'panda' is not fully loaded!")
    raise NameError('One of the required devices is not loaded : %s, please check!' % e)

if focibox.read(0) == 'Cu':
    from nicos import session
    mfh.alias = session.getDevice('mfh_cu')
    mfv.alias = session.getDevice('mfv_cu')
    mono.alias = session.getDevice('mono_cu')
    ana.alias = session.getDevice('ana_pg')
    mfh.motor._pushParams() # forcibly send parameters to HW
    mfv.motor._pushParams() # forcibly send parameters to HW
    focibox.comm('XMA',forcechannel=False) # enable output for mfh
    focibox.comm('YMA',forcechannel=False) # enable output for mfv
    focibox.driverenable = True
    maw(mtx, 0) #correct center of rotation for Si-mono only
    del session
else:
    printerror('WRONG MONO ON TABLE FOR SETUP mono_cu !!!')
'''
