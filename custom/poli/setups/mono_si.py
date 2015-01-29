description = 'POLI silicon monochromator'

group = 'optional'

includes = ['mono', ]

excludes = ['mono_cu', ]

nethost = 'slow.poli.frm2'

devices = dict(
    sih = device('devices.taco.Motor',
                 description = 'Silicon monochromator horizontal focus',
                 tacodevice = '//%s/poli/fzjs7/sih' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (0, 10),
                ),
    siv = device('devices.taco.Motor',
                 description = 'Silicon monochromator vertical focus',
                 tacodevice = '//%s/poli/fzjs7/siv' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (0, 10),
                ),
)

startupcode = """
"""
