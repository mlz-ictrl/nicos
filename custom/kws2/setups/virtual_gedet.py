# Setup for the GE detector
description = 'large GE He-3 detector (virtual)'
group = 'lowlevel'
display_order = 24

eps = configdata('config_gedet.EIGHT_PACKS')
hv_values = configdata('config_gedet.HV_VALUES')

devices = dict(
    ep_HV_all = device('kws2.gedet.MultiHV',
                       ephvs = [epname + '_HV' for (epname, _) in eps],
                       lowlevel = True,
                       stepsettle = 2,
                       finalsettle = 30,
                      ),
    gedet_HV  = device('kws2.gedet.HVSwitcher',
                       description = 'switches the GE detector HV',
                       moveable = 'ep_HV_all',
                       mapping = {
                           'off': (0,) * 18,
                           'on':  tuple(hv_values[n[0]] for n in eps),
                       },
                       pv_values = {},
                       fallback = 'inbetween',
                       precision = 25,
                      ),
    gedet_power = device('devices.generic.ManualSwitch',
                         description = 'switches the GE detector 54V power supply',
                         states = ['off', 'on'],
                        ),
)


for (epname, _) in eps:
    devices[epname + '_HV'] = device('kws1.virtual.Standin',
                                     description = epname + ' HV setting',
                                     lowlevel = True)
