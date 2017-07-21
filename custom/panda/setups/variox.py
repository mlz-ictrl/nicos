#  -*- coding: utf-8 -*-

description = 'Variox from Panda with labview-control'

includes = ['alias_T']

excludes = ['15T']

group = 'optional'

devices = dict(

# DONT change names or the labview part wont work anymore !!!!!
    vti = device('nicos.devices.generic.CacheWriter',
                 description = 'variable Temperature Insert',
                 userlimits = (1, 200),
                 abslimits = (0, 311),
                 fmtstr = '%.3f',
                 unit = 'K',
                 loopdelay = 5,
                 window = 60,
                 maxage = 30,
                 precision = 0.2,
                ),
    sTs = device('nicos.devices.generic.CacheReader',
                 description = 'Sample Temperature',
                 fmtstr = '%.3f',
                 unit = 'K',
                 maxage = 30,
                ),
    LN2 = device('nicos.devices.generic.CacheReader',
                 description = 'Level of Liquid Nitrogen',
                 fmtstr = '%.1f',
                 unit = '%',
                 maxage = 300,
                ),
    LHe = device('nicos.devices.generic.CacheReader',
                 description = 'Level of Liquid Helium',
                 fmtstr = '%.1f',
                 unit = '%',
                 maxage = 900,
                ),
    NV  = device('nicos.devices.generic.CacheWriter',
                 description = 'Position of Needlevalve controlling cooling of vti',
                 userlimits = (0, 99.9),
                 abslimits = (0, 99.9),
                 fmtstr = '%.1f',
                 unit = '%',
                 maxage = 30,
                 window = 20,
                 loopdelay = 5,
                 precision = 0.1,
                ),
    vti_pressure = device('nicos.devices.generic.CacheWriter',
                 description = 'Regulated pressure on Needle valve',
                 userlimits = (0, 200),
                 abslimits = (0, 200),
                 fmtstr = '%.1f',
                 unit = 'mbar',
                 maxage = 30,
                 window = 20,
                 loopdelay = 5,
                 precision = 0.1,
                ),
    #~ vti_pressure = device('nicos.devices.generic.CacheReader',
                 #~ description = 'Actual pressure on Needle valve',
                 #~ fmtstr = '%.1f',
                 #~ unit = 'mbar',
                 #~ maxage = 30,
                #~ ),
)

# alias_config = {
#     'T': {'vti': 200},
#     'Ts': {'sTs': 100},
# }
