description = 'PANDA PG-monochromator'

group = 'lowlevel'

includes = ['monofoci', 'monoturm', 'panda_mtt']

excludes = ['mono_si', 'mono_cu', 'mono_heusler']

extended = dict(dynamic_loaded = True)

devices = dict(
    mono_pg = device('nicos.devices.tas.Monochromator',
        description = 'PG Monochromator of PANDA',
        unit = 'A-1',
        theta = 'mth',
        twotheta = 'mtt',
        reltheta = True,
        focush = 'mfh_pg',
        focusv = 'mfv_pg',
        hfocuspars = [306.91, -4.0565, 0.1346],
        hfocusflat = 343.9,
        vfocuspars = [327.8,  -215.59, 66.843, -9.6554, 0.5228],
        vfocusflat = 150,
        abslimits = (1, 10),
        dvalue = 3.355,
        scatteringsense = -1,
        crystalside = -1,
    ),
    mfh_pg_step = device('nicos_virt_mlz.panda.devices.stubs.MccMotor',
        description = 'horizontal focusing MOTOR of PG monochromator',
        fmtstr = '%.3f',
        abslimits = (-400, 400),
        userlimits = (-360, 360),
        unit = 'deg',
        speed = 5,
        lowlevel = True,
        curvalue = 20,
    ),
    mfh_pg = device('nicos_mlz.panda.devices.rot_axis.RotAxis',
        description = 'horizontal focus of PG monochromator',
        motor = 'mfh_pg_step',
        precision = 1,
        refpos = 208.75,
        refspeed = 1.5,
        autoref = -10,  # autoref every 10 full turns
    ),
    mfv_pg_step = device('nicos_virt_mlz.panda.devices.stubs.MccMotor',
        description = 'vertical focusing MOTOR of PG monochromator',
        fmtstr = '%.3f',
        abslimits = (-400, 400),
        userlimits = (-360, 360),
        unit = 'deg',
        speed = 5,
        lowlevel = True,
    ),
    mfv_pg = device('nicos_mlz.panda.devices.rot_axis.RotAxis',
        description = 'vertical focus of PG monochromator',
        motor = 'mfv_pg_step',
        precision = 1,
        refpos = 221.3,
        refspeed = 1.5,
        autoref = -10,  # autoref every 10 full turns
    ),
)

startupcode = '''
from nicos import session
from nicos.core import SIMULATION

try:
    _ = (ana, mono, mfv, mfh, focibox)
except NameError as e:
    printerror("The requested setup 'panda' is not fully loaded!")
    raise NameError('One of the required devices is not loaded : %s, please check!' % e)

if session.mode == SIMULATION:
    mfh.alias = session.getDevice('mfh_pg')
    mfv.alias = session.getDevice('mfv_pg')
    mono.alias = session.getDevice('mono_pg')
    ana.alias = session.getDevice('ana_pg')
elif focibox.read(0) == 'PG':
    mfh.alias = session.getDevice('mfh_pg')
    mfv.alias = session.getDevice('mfv_pg')
    mono.alias = session.getDevice('mono_pg')
    ana.alias = session.getDevice('ana_pg')
    mfh.motor._pushParams() # forcibly send parameters to HW
    mfv.motor._pushParams() # forcibly send parameters to HW
    focibox.comm('XMA', forcechannel=False) # enable output for mfh
    focibox.comm('YMA', forcechannel=False) # enable output for mfv
    focibox.driverenable = True
    #maw(mtx, 0) #correct center of rotation for Si-mono only
else:
    printerror('WRONG MONO ON TABLE FOR SETUP mono_pg !!!')
del session
'''

extended = dict(
    poller_cache_reader = ['mtt'],
)
