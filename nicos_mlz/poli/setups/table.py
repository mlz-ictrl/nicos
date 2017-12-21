description = 'POLI sample table'

group = 'lowlevel'

includes = ['alias_sth']

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    omega = device('nicos.devices.tango.Motor',
        description = 'table omega axis',
        tangodevice = tango_base + 'fzjs7/omega',
        abslimits = (-180, 180),
        unit = 'deg',
        fmtstr = '%.2f',
        precision = 0.005,
    ),
    gamma = device('nicos.devices.tango.Motor',
        description = 'table gamma axis',
        tangodevice = tango_base + 'fzjs7/gamma',
        abslimits = (-20, 130),
        unit = 'deg',
        fmtstr = '%.2f',
        precision = 0.005,
    ),
    chi1 = device('nicos.devices.tango.Motor',
        description = 'table chi1 axis',
        tangodevice = tango_base + 'fzjs7/chi1',
        abslimits = (-5, 5),
        unit = 'deg',
        fmtstr = '%.2f',
        precision = 0.005,
    ),
    chi2 = device('nicos.devices.tango.Motor',
        description = 'table chi2 axis',
        tangodevice = tango_base + 'fzjs7/chi2',
        abslimits = (-5, 5),
        unit = 'deg',
        fmtstr = '%.2f',
        precision = 0.005,
    ),
    xtrans = device('nicos.devices.tango.Motor',
        description = 'table x translation axis',
        tangodevice = tango_base + 'fzjs7/xtrans',
        abslimits = (-15, 15),
        unit = 'mm',
        fmtstr = '%.2f',
        precision = 0.01,
    ),
    ytrans = device('nicos.devices.tango.Motor',
        description = 'table y translation axis',
        tangodevice = tango_base + 'fzjs7/ytrans',
        abslimits = (-15, 15),
        unit = 'mm',
        fmtstr = '%.2f',
        precision = 0.01,
    ),
)

alias_config = {
    'sth': {'omega': 100}
}
