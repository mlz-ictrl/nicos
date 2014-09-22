description = 'POLI monochromator devices'

group = 'lowlevel'

includes = ['mono_cu', 'mono_si']

nethost = 'slow.poli.frm2'

devices = dict(
    chi_m     = device('devices.taco.Motor',
                       description = 'monochromator tilt (chi axis)',
                       tacodevice = '//%s/poli/fzjs7/chi_m' % (nethost, ),
                       pollinterval = 15,
                       maxage = 61,
                       fmtstr = '%.2f',
                       abslimits = (0, 12700),
                      ),
    theta_m   = device('devices.taco.Motor',
                       description = 'monochromator rotation (theta axis)',
                       tacodevice = '//%s/poli/fzjs7/theta_m' % (nethost, ),
                       pollinterval = 15,
                       maxage = 61,
                       fmtstr = '%.2f',
                       abslimits = (0, 1300000),
                      ),
    x_m       = device('devices.taco.Motor',
                       description = 'monochromator translation (x axis)',
                       tacodevice = '//%s/poli/fzjs7/x_m' % (nethost, ),
                       pollinterval = 15,
                       maxage = 61,
                       fmtstr = '%.2f',
                       abslimits = (0, 90000),
                      ),
    changer_m = device('devices.taco.Motor',
                       description = 'monochromator changer axis',
                       tacodevice = '//%s/poli/fzjs7/change_m' % (nethost, ),
                       pollinterval = 15,
                       maxage = 61,
                       fmtstr = '%.2f',
                       abslimits = (0, 4000000),
                      ),
    h_m       = device('devices.generic.DeviceAlias',
                       description = 'horizontal monochromator focus',
                      ),
    v_m       = device('devices.generic.DeviceAlias',
                       description = 'vertical monochromator focus',
                      ),
    h_m_alias = device('devices.generic.ParamDevice',
                       lowlevel = True,
                       device = 'h_m',
                       parameter = 'alias',
                      ),
    v_m_alias = device('devices.generic.ParamDevice',
                       lowlevel = True,
                       device = 'v_m',
                       parameter = 'alias',
                      ),
    mono      = device('poli.mono.MultiSwitcher',
                       description = 'monochromator wavelength switcher',
                       # note: precision of chi and theta is so large because they are expected
                       # to be changed slightly depending on setup
                       moveables = ['x_m', 'changer_m', 'chi_m', 'theta_m', 'h_m_alias', 'v_m_alias'],
                       precision = [10,    10,          5000,    10000,     None,        None],
                       mapping = {
                           0.9:  [38000, 190000, 6300, 236000, 'cuh', 'cuv'],
                           1.14: [45000, 3790,   8600, 236000, 'sih', 'siv'],
                       },
                       changepos = 0,
                      ),
)

startupcode = """
"""
