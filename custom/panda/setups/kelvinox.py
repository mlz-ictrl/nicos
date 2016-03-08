#  -*- coding: utf-8 -*-

description = 'Kelvinox from Panda with labview-control'

group = 'optional'

includes = ['alias_T']

devices = dict(
    # DONT CHANGE THESE NAMES OR THE LABVIEW PART WONT WORK ANYMORE !
    mc        = device('devices.generic.cache.CacheWriter',
                       description = 'Mixing chamber temperature',
                       userlimits=( 0.01, 6 ),
                       abslimits = (0.01, 6 ),
                       fmtstr = '%.3f',
                       unit = 'K',
                       loopdelay = 5,
                       window = 60,
                       maxage = 30,
                       precision = 0.01,
                      ),
    sorb      = device('devices.generic.cache.CacheWriter',
                       description = 'Temperature of Sorb pump',
                       userlimits=( 4, 250 ),
                       abslimits = (4, 250 ),
                       fmtstr = '%.2f',
                       unit = 'K',
                       loopdelay = 5,
                       window = 60,
                       maxage = 30,
                       precision = 1.0,
                      ),
    onekpot   = device('devices.generic.cache.CacheReader',
                       description = 'Temperature of precooling stage (1K-pot)',
                       fmtstr = '%.3f',
                       unit = 'K',
                       maxage = 30,
                      ),
    igh_p1   = device('devices.generic.cache.CacheReader',
                      description = 'Pressure P1 of IGH',
                      fmtstr = '%.3f',
                      unit = 'mbar',
                      maxage = 30,
                     ),
    igh_p2   = device('devices.generic.cache.CacheReader',
                      description = 'Pressure P2 of IGH',
                      fmtstr = '%.3f',
                      unit = 'mbar',
                      maxage = 30,
                     ),
    igh_g1   = device('devices.generic.cache.CacheReader',
                      description = 'Pressure G1 of IGH',
                      fmtstr = '%.3f',
                      unit = 'mbar',
                      maxage = 30,
                     ),
    igh_g2   = device('devices.generic.cache.CacheReader',
                      description = 'Pressure G2 of IGH',
                      fmtstr = '%.3f',
                      unit = 'mbar',
                      maxage = 30,
                     ),
    igh_g3   = device('devices.generic.cache.CacheReader',
                      description = 'Pressure G3 of IGH',
                      fmtstr = '%.3f',
                      unit = 'mbar',
                      maxage = 30,
                     ),
)

alias_config = {
    'T': {'mc': 200},
    'Ts': {'mc': 100},
}
