description = 'PANDA Heusler-analyzer'

group = 'lowlevel'

includes = ['monofoci', 'monoturm', 'panda_s7']
excludes = []

modules = []

extended = dict(dynamic_loaded = True)

# for ipc-stuff
MOTOR = lambda x: 0x50 + x
devices = dict(
    ana_heusler      = device('devices.tas.Monochromator',
                              description = 'PANDA\'s Heusler ana',
                              unit = 'A-1',
                              theta = 'ath',
                              twotheta = 'att',
                              focush = 'afh_heusler',
                              focusv = None,
                              abslimits = (1, 10),
                              #hfocuspars = [44.8615, 4.64632, 2.22023], #2009
                              #hfocuspars = [-66.481, 36.867, -2.8148], #2013-11
                              hfocuspars = [-478,483.74,-154.68,16.644], #2013-11 2nd
                              dvalue = 3.45,
                              scatteringsense = -1,
                              crystalside = -1,
                             ),
    afh_heusler_step = device('devices.vendor.ipc.Motor',
                              description = 'stepper for horizontal focus of heusler ana',
                              bus = 'bus1',
                              addr = MOTOR(8),
                              confbyte = 136,
                              slope = 400 / 360.0,
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
    afh_heusler  = device('panda.rot_axis.RotAxis',
                          description = 'horizontal focus of heusler ana',
                          motor = 'afh_heusler_step',
                          coder = 'afh_heusler_step',
                          dragerror = 5,
                          abslimits = (-179, 179),
                          obs = [],
                          precision = 1,
                          fmtstr = '%.1f',
                          autoref = None, # disable autoref since there is no refswitch
                          lowlevel = True,
                         ),
)

startupcode = '''
try:
    _ = (ana, mono, mfv, mfh, focibox)
except NameError as e:
    printerror("The requested setup 'panda' is not fully loaded!")
    raise NameError('One of the required devices is not loaded : %s, please check!' % e)

    from nicos import session
    ana.alias = session.getDevice('ana_heusler')
    afh.alias = session.getDevice('afh_heusler')
    del session
'''
