#  -*- coding: utf-8 -*-

description = 'Variox from Panda with labview-control'

includes = ['alias_T']

excludes = ['15T']

group = 'optional'

devices = dict(

# DONT change names or the labview part wont work anymore !!!!!
    vti = device('devices.generic.cache.CacheWriter',
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
    sTs = device('devices.generic.cache.CacheReader',
                 description = 'Sample Temperature',
                 fmtstr = '%.3f',
                 unit = 'K',
                 maxage = 30,
                ),
    LN2 = device('devices.generic.cache.CacheReader',
                 description = 'Level of Liquid Nitrogen',
                 fmtstr = '%.1f',
                 unit = '%',
                 maxage = 300,
                ),
    LHe = device('devices.generic.cache.CacheReader',
                 description = 'Level of Liquid Helium',
                 fmtstr = '%.1f',
                 unit = '%',
                 maxage = 900,
                ),
    NV  = device('devices.generic.cache.CacheReader',
                 description = 'Position of Needlevalve controlling cooling of vti',
                 fmtstr = '%.1f',
                 unit = '%',
                 maxage = 30,
                ),
)

startupcode = '''
T.alias='vti'
Ts.alias='sTs'
'''
