description = 'PANDA Si-monochromator'

group = 'optional'

includes = ['panda', 'focibox']

modules = []

excludes = ['mono_pg', 'mono_cu', 'mono_heusler']

devices = dict(
    mono_si     = device('devices.tas.Monochromator',
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
                         dvalue = 3.455,
                         scatteringsense = -1,
                        ),
    mfh_si_step = device('panda.mcc2.MCC2Motor',
                         description = 'horizontal focusing MOTOR of Si monochromator',
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
                        ),
    mfh_si_enc  = device('panda.mcc2.MCC2Coder',
                         description = 'horizontal focusing CODER of Si monochromator',
                         bus = 'focimotorbus',
                         fmtstr = '%.3f',
                         channel = 'X',
                         addr = 0,
                         slope = 27000.0 / 5, #???
                         unit = 'mm',
                         zerosteps = 0,
                         codertype = 'incremental',
                         coderbits = 25,
                         lowlevel = True,
                        ),
    mfh_si      = device('nicos.devices.generic.Axis',
                         description = 'horizontal focus of Si monochromator',
                         motor = 'mfh_si_step',
                         coder = 'mfh_si_enc',
                         obs = [],
                         precision = 0.01,
                         backlash = 0,
                         lowlevel = True,
                        ),
)

startupcode = """
if focibox.read(0) == 'Si':
        mfh.alias = mfh_si
        mfv.alias = None
        mono.alias = mono_si
        ana.alias = ana_pg
        mfh_si_step._pushParams() # forcibly send parameters to HW
        focibox.com('XME',forcechannel=False) # enable output for mfh
        #focibox.com('YME',forcechannel=False) # enable output for mfv
        focibox.driverenable = True
        #maw(mtx, -12)
else:
        printerror('WRONG MONO ON TABLE FOR SETUP mono_si !!!')
"""