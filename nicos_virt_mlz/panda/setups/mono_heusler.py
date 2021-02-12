description = 'PANDA Heusler-monochromator'

group = 'lowlevel'

includes = ['monofoci', 'monoturm', 'panda_mtt']
excludes = ['mono_pg', 'mono_cu', 'mono_si', 'ana_heusler']

extended = dict(dynamic_loaded = True)

devices = dict(
    mono_heusler = device('nicos.devices.tas.Monochromator',
        description = 'PANDA Heusler monochromator',
        unit = 'A-1',
        theta = 'mth',
        twotheta = 'mtt',
        reltheta = True,
        focush = None,
        focusv = 'mfv_heusler',
        hfocuspars = [0],
        vfocuspars = [303.0, -141.39, 27.855, -1.8127],  # 2013-11 2nd
        abslimits = (1, 10),
        dvalue = 3.45,
        scatteringsense = -1,
        crystalside = -1,
    ),

    mfv_heusler_step = device('nicos_virt_mlz.panda.devices.stubs.MccMotor',
        description = 'vertical focusing MOTOR of Heusler monochromator',
        fmtstr = '%.3f',
        abslimits = (-360, 360),
        userlimits = (-4, 360),
        unit = 'deg',
        speed = 20,
        lowlevel = True,
    ),
    mfv_heusler = device('nicos_mlz.panda.devices.rot_axis.RefAxis',
        description = 'vertical focus of Heusler monochromator',
        motor = 'mfv_heusler_step',
        precision = 0.1,
        backlash = 0,
        refpos = -44,
        lowlevel = True,
        autoref = -10,
    ),

    ana_heusler = device('nicos.devices.tas.Monochromator',
        description = 'PANDA\'s Heusler ana',
        unit = 'A-1',
        theta = 'ath',
        twotheta = 'att',
        focush = 'afh_heusler',
        focusv = None,
        abslimits = (1, 10),
        # hfocuspars = [44.8615, 4.64632, 2.22023],  # 2009
        # hfocuspars = [-66.481, 36.867, -2.8148],   # 2013-11
        hfocuspars = [-478, 483.74, -154.68, 16.644],  # 2013-11 2nd
        dvalue = 3.45,
        scatteringsense = -1,
        crystalside = -1,
    ),
    afh_heusler_step = device('nicos.devices.generic.VirtualMotor',
        description = 'stepper for horizontal focus of heusler ana',
        unit = 'deg',
        abslimits = (-179, 179),
        speed = 1,
        lowlevel = True,
    ),
    afh_heusler = device('nicos_mlz.panda.devices.rot_axis.RotAxis',
        description = 'horizontal focus of heusler ana',
        motor = 'afh_heusler_step',
        dragerror = 5,
        abslimits = (-179, 179),
        precision = 1,
        fmtstr = '%.1f',
        autoref = None,  # disable autoref since there is no refswitch
        lowlevel = True,
    ),
)

startupcode = '''
try:
    _ = (ana, mono, mfv, mfh, focibox)
except NameError as e:
    printerror("The requested setup 'panda' is not fully loaded!")
    raise NameError('One of the required devices is not loaded : %s, please check!' % e)

if focibox.read(0) == 'Heusler':
    from nicos import session
    mfh.alias = None
    mfv.alias = session.getDevice('mfv_heusler')
    mono.alias = session.getDevice('mono_heusler')
    ana.alias = session.getDevice('ana_heusler')
    afh.alias = session.getDevice('afh_heusler')
    #mfh.motor._pushParams() # forcibly send parameters to HW
    mfv.motor._pushParams() # forcibly send parameters to HW
    #focibox.comm('XMA',forcechannel=False) # enable output for mfh
    focibox.comm('YMA',forcechannel=False) # enable output for mfv
    focibox.driverenable = True
    #maw(mtx, 0) #correct center of rotation for Si-mono only
    del session
else:
    printerror('WRONG MONO ON TABLE FOR SETUP mono_heusler !!!')
'''
