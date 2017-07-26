description = 'PANDA Si-monochromator'

group = 'lowlevel'

includes = ['monofoci', 'monoturm', 'panda_s7']

modules = []

excludes = ['mono_pg', 'mono_cu', 'mono_heusler']

extended = dict(dynamic_loaded = True)

devices = dict(
    mono_si     = device('nicos.devices.tas.Monochromator',
                         description = 'PANDA Si monochromator',
                         unit = 'A-1',
                         theta = 'mth',
                         twotheta = 'mtt',
                         reltheta = True,
                         focush = 'mfh_si',
                         focusv =  None,
                         hfocuspars = [0],
                         vfocuspars = [0],
                         abslimits = (1, 10),
                         userlimits = (1, 10),
                         dvalue = 3.455,
                         scatteringsense = -1,
                         crystalside = -1,
                        ),
    mfh_si_step = device('nicos_mlz.panda.devices.mcc2.MCC2Motor',
                         description = 'horizontal focusing MOTOR of Si monochromator',
                         bus = 'focimotorbus',
                         mccmovement = 'linear',
                         precision = 0.01,
                         fmtstr = '%.3f',
                         channel = 'X',
                         addr = 0,
                         slope = 27000.0 / 5 * 200 / 512,
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
                        ),
    mfh_si_enc  = device('nicos_mlz.panda.devices.mcc2.MCC2Coder',
                         description = 'horizontal focusing CODER of Si monochromator',
                         bus = 'focimotorbus',
                         fmtstr = '%.3f',
                         channel = 'X',
                         addr = 0,
                         slope = 4 * 27000.0 / 5, #???
                         unit = 'mm',
                         zerosteps = 0,
                         codertype = 'incremental',
                         coderbits = 25,
                         lowlevel = True,
                        ),
    #~ mfh_si      = device('nicos.devices.generic.Axis',
    mfh_si      = device('nicos_mlz.panda.devices.rot_axis.RefAxis',
                         description = 'horizontal focus of Si monochromator',
                         motor = 'mfh_si_step',
                         coder = 'mfh_si_enc',
                         obs = [],
                         precision = 0.01,
                         backlash = -0.2,
                         refpos = 1.4,
                         refspeed = 0.01,
                         autoref = None,
                        ),
)

startupcode = '''
try:
    _ = (ana, mono, mfv, mfh, focibox)
except NameError as e:
    printerror("The requested setup 'panda' is not fully loaded!")
    raise NameError('One of the required devices is not loaded : %s, please check!' % e)

if focibox.read(0) == 'Si':
    from nicos import session
    mfh.alias = session.getDevice('mfh_si')
    mfv.alias = None
    mono.alias = session.getDevice('mono_si')
    ana.alias = session.getDevice('ana_pg')
    mfh.motor._pushParams() # forcibly send parameters to HW
    #mfv.motor._pushParams() # forcibly send parameters to HW
    focibox.comm('XMA',forcechannel=False) # enable output for mfh
    #focibox.comm('YMA',forcechannel=False) # enable output for mfv
    focibox.driverenable = True
    #maw(mtx, -12) #correct center of rotation for Si-mono only
    del session
else:
    printerror('WRONG MONO ON TABLE FOR SETUP mono_si !!!')
'''
