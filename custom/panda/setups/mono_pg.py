description = 'PANDA PG-monochromator'

group = 'optional'

includes = ['panda', 'focibox']

modules = []

excludes = ['mono_si', 'mono_cu', 'mono_heusler']

devices = dict(
    mono_pg     = device('devices.tas.Monochromator',
                         description = 'PG Monochromator of PANDA',
                         unit = 'A-1',
                         theta = 'mth',
                         twotheta = 'mtt',
                         reltheta = True,
                         focush = 'mfh_pg',
                         focusv = 'mfv_pg',
                         hfocuspars = [294.28075, -5.3644, -0.1503],
                         vfocuspars = [418.22, -326.12, 116.331, -19.0842, 1.17283],
                         abslimits = (1, 10),
                         dvalue = 3.355,
                         scatteringsense = -1,
                        ),
    mfh_pg_step = device('panda.mcc2.MCC2Motor',
                         description = 'horizontal focusing MOTOR of PG monochromator',
                         bus = 'focimotorbus',
                         mccmovement = 'linear',
                         precision = 0.01,
                         fmtstr = '%.3f',
                         channel = 'X',
                         addr = 0,
                         slope = 900*24*2/360., # 900:1 gear, 24 steps per rev, 360deg per rev
                         abslimits = (-400,400),
                         userlimits = (0,340),
                         unit = 'deg',
                         idlecurrent = 0.1,
                         movecurrent = 0.2,
                         rampcurrent = 0.25,
                         microstep = 2,
                         speed = 1.5,
                         accel = 50,
                         lowlevel = True,
                        ),
    mfh_pg      = device('panda.rot_axis.RotAxis',
                         description = 'horizontal focus of PG monochromator',
                         motor = 'mfh_step',
                         coder = 'mfh_step',
                         obs = [],
                         precision = 1,
                         refpos = 208.75,
                         refspeed = 5,
                         autoref = -10, # autoref every 10 full turns
                        ),
    mfv_pg_step = device('panda.mcc2.MCC2Motor',
                         description = 'vertical focusing MOTOR of PG monochromator',
                         bus = 'focimotorbus',
                         mccmovement = 'linear',
                         precision = 0.01,
                         fmtstr = '%.3f',
                         channel = 'Y',
                         addr = 0,
                         slope = 900*24*2/360., # 900:1 gear, 24 steps per rev, 360deg per rev
                         abslimits = (-400,400),
                         userlimits = (0,340),
                         unit = 'deg',
                         idlecurrent = 0.1,
                         movecurrent = 0.2,
                         rampcurrent = 0.25,
                         microstep = 2,
                         speed = 5,
                         accel = 50,
                         lowlevel = True,
                        ),
    mfv_pg      = device('panda.rot_axis.RotAxis',
                         description = 'vertical focus of PG monochromator',
                         motor = 'mfh_step',
                         coder = 'mfh_step',
                         obs = [],
                         precision = 1,
                         refpos = 221.3,
                         refspeed = 1.5,
                         autoref = -10, # autoref every 10 full turns
                        ),
)

startupcode = """
if focibox.read(0) == 'PG':
        mfh.alias = mfh_pg
        mfv.alias = mfv_pg
        mono.alias = mono_pg
        ana.alias = ana_pg
        mfh_pg_step._pushParams() # forcibly send parameters to HW
        mfv_pg_step._pushParams()
        focibox.com('XME',forcechannel=False) # enable output
        focibox.com('YME',forcechannel=False) # enable output
        focibox.driverenable = True
        maw(mtx, 0)
else:
        printerror('WRONG MONO ON TABLE FOR SETUP mono_pg !!!')
"""