# Setup for the GE detector
description = 'large GE He-3 detector'
group = 'lowlevel'
display_order = 24

excludes = ['virtual_gedet']

eps = configdata('config_gedet.EIGHT_PACKS')
hv_values = configdata('config_gedet.HV_VALUES')
pv_common = configdata('config_gedet.PV_VALUES_COMMON')
pv_single = configdata('config_gedet.PV_VALUES_SINGLE')
pv_scales = configdata('config_gedet.PV_SCALES')

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

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
                           'off': (0,) * len(eps),
                           'on':  tuple(hv_values[n[0]] for n in eps),
                       },
                       pv_values = {
                           epicsid: pv_common + pv_single[epname] + pv_scales[epname]
                           for (epname, epicsid) in eps
                       },
                       fallback = 'inbetween',
                       precision = 25,
                      ),
)


for (epname, epicsid) in eps:
    devices[epname + '_T']  = device('devices.epics.EpicsReadable',
                                     description = epname + ' FPGA temperature',
                                     readpv = epicsid + ':FpgaTemperature',
                                     lowlevel = True,
                                     unit = 'degC',
                                     pollinterval = 10,
                                     fmtstr = '%.1f',
                                     warnlimits = (25, 75))
    devices[epname + '_TB'] = device('devices.epics.EpicsReadable',
                                     description = epname + ' board temperature',
                                     readpv = epicsid + ':RsppTemperature',
                                     lowlevel = True,
                                     unit = 'degC',
                                     pollinterval = 10,
                                     fmtstr='%.1f',
                                     warnlimits = (25, 45))
    devices[epname + '_HV'] = device('devices.epics.EpicsAnalogMoveable',
                                     description = epname + ' HV setting',
                                     readpv = epicsid + ':HighVoltage_R',
                                     writepv = epicsid + ':HighVoltage_W',
                                     lowlevel = True,
                                     unit = 'V',
                                     pollinterval = 10,
                                     fmtstr = '%.0f',
                                     warnlimits = (1520, 1540))

for ti in range(1, 3):
    devices['ps%d_V' % ti] = device('devices.tango.PowerSupply',
                                    description = 'detector power supply voltage',
                                    tangodevice = tango_base + 'gesupply/ps%d' % ti,
                                    unit = 'V',
                                    abslimits = (0, 54),
                                    userlimits = (0, 54),
                                    warnlimits = (53.9, 54.1))
    devices['ps%d_I' % ti] = device('devices.generic.ReadonlyParamDevice',
                                    description = 'detector power supply current',
                                    device = 'ps%d_V' % ti,
                                    parameter = 'current',
                                    unit = 'A',
                                    warnlimits = (2.8, 3.2))
