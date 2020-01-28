description = 'PANDA virtual monochromator'

group = 'lowlevel'

includes = ['monoturm']

excludes = ['mono_si', 'mono_cu', 'mono_heusler', 'mono_pg']

extended = dict(dynamic_loaded = True)

devices = dict(
    mono_virtual = device('nicos.devices.tas.Monochromator',
        description = 'Virtual Monochromator for PANDA',
        unit = 'A-1',
        theta = 'mth_virtual',
        twotheta = 'mtt',
        reltheta = True,
        focush = None,
        focusv = None,
        abslimits = (1, 10),
        dvalue = 3.355,
        scatteringsense = -1,
        crystalside = -1,
    ),
    mth_virtual = device('nicos.devices.generic.VirtualMotor',
        description = 'Virtual mth',
        abslimits = (-180, 180),
        unit = 'deg',
    ),
    mfh_virtual = device('nicos.devices.generic.VirtualMotor',
        description = 'Virtual mfh',
        abslimits = (1, 10),
        unit = 'deg',
    ),
    mfv_virtual = device('nicos.devices.generic.VirtualMotor',
        description = 'Virtual mfv',
        abslimits = (-400, 400),
        unit = 'deg',
    ),
)

startupcode = '''
mono.alias = mono_virtual
mfh.alias = mfh_virtual
mfv.alias = mfv_virtual
'''

extended = dict(
    poller_cache_reader = ['mtt'],
)
