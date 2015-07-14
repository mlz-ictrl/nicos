description = 'POLI copper monochromator devices'

group = 'optional'

excludes = ['mono_si']

tango_host = 'tango://phys.poli.frm2:10000'

devices = dict(
    cuh = device('devices.tango.Motor',
                 lowlevel = False,
                 description = 'Copper monochromator horizontal focus',
                 tangodevice = '%s/poli/fzjs7/cuh' % (tango_host, ),
                 fmtstr = '%.2f',
                ),
    cuv = device('devices.tango.Motor',
                 lowlevel = False,
                 description = 'Copper monochromator vertical focus',
                 tangodevice = '%s/poli/fzjs7/cuv' % (tango_host, ),
                 fmtstr = '%.2f',
                ),
)

startupcode = """
"""
