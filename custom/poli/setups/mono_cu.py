description = 'POLI copper monochromator devices'

group = 'lowlevel'

nethost = 'slow.poli.frm2'

devices = dict(
    cuh = device('devices.taco.Motor',
                 lowlevel = True,
                 description = 'Copper monochromator horizontal focus',
                 tacodevice = '//%s/poli/fzjs7/cuh' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (-75, 75),
                ),
    cuv = device('devices.taco.Motor',
                 lowlevel = True,
                 description = 'Copper monochromator vertical focus',
                 tacodevice = '//%s/poli/fzjs7/cuv' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (0, 171.2),
                ),
)

startupcode = """
"""
