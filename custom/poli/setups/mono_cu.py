description = 'POLI copper monochromator'

group = 'optional'

includes = ['mono', ]

excludes = ['mono_si', ]

nethost = 'slow.poli.frm2'

devices = dict(
    cuh = device('devices.taco.Motor',
                 description = 'Copper monochromator horizontal focus',
                 tacodevice = '//%s/poli/fzjs7/cuh' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (0, 10),
                ),
    cuv = device('devices.taco.Motor',
                 description = 'Copper monochromator vertical focus',
                 tacodevice = '//%s/poli/fzjs7/cuv' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (0, 10),
                ),
)

startupcode = """
"""
