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

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    ep_HV_all = device('nicos_mlz.kws1.devices.gedet.MultiHV',
        ephvs = [epname + '_HV' for (epname, _) in eps],
        lowlevel = True,
        stepsettle = 3,
        finalsettle = 90,
    ),
    gedet_HV = device('nicos_mlz.kws1.devices.gedet.HVSwitcher',
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

    gedet_power = device('nicos.devices.generic.MultiSwitcher',
        description = 'switches the GE detector 54V power supply',
        moveables = ['ps1_V', 'ps2_V'],
        mapping = {
            'off': [0, 0],
            'on': [54, 54],
        },
        precision = [0.1, 0.1],
        warnlimits = ('on', 'on'),  # should always be on
        fallback = 'unknown',
    ),
)

for (epname, epicsid) in eps: # + [('ep09x', 'GE-D7561E-EP')]:
    devices[epname + '_T'] = device('nicos.devices.epics.EpicsReadable',
        description = epname + ' FPGA temperature',
        readpv = epicsid + ':FpgaTemperature',
        lowlevel = True,
        unit = 'degC',
        pollinterval = 10,
        fmtstr = '%.1f',
        warnlimits = (25, 75),
    )
    devices[epname + '_TB'] = device('nicos.devices.epics.EpicsReadable',
        description = epname + ' board temperature',
        readpv = epicsid + ':RsppTemperature',
        lowlevel = True,
        unit = 'degC',
        pollinterval = 10,
        fmtstr = '%.1f',
        warnlimits = (25, 45),
    )
    devices[epname + '_HV'] = device('nicos_mlz.kws1.devices.gedet.'
        'HVEpicsAnalogMoveable',
        description = epname + ' HV setting',
        readpv = epicsid + ':HighVoltage_R',
        writepv = epicsid + ':HighVoltage_W',
        lowlevel = True,
        unit = 'V',
        pollinterval = 10,
        fmtstr = '%.0f',
        abslimits = (0, 1600),
        warnlimits = (1520, 1540),
    )
    devices[epname + '_HV_SP'] = device('nicos.devices.epics.EpicsReadable',
        description = epname + ' HV setting',
        readpv = epicsid + ':HighVoltage_W',
        lowlevel = True,
        unit = 'V',
        pollinterval = 10,
        fmtstr = '%.0f',
    )
    devices[epname + '_cts'] = device('nicos_mlz.kws1.devices.gedet.HVEpicsArrayReadable',
        description = epname + ' tube counts',
        readpv = epicsid + ':TubeCounts',
        lowlevel = True,
    )

#devices['ep10_P'] = device('nicos.devices.tango.AnalogInput',
#                           tangodevice = tango_base + 'ep10/power',
#                           description = 'ep10 delivered PoE power',
#                           lowlevel = True,)
#devices['ep10_cts'] = device('nicos_mlz.kws1.devices.gedet.HVEpicsArrayReadable',
#                             readpv = 'GE-D72EA6-EP:TubeCounts',
#                             lowlevel = True,)
#devices['ep07_cts'] = device('nicos_mlz.kws1.devices.gedet.HVEpicsArrayReadable',
#                             readpv = 'GE-D72F9D-EP:TubeCounts',
#                             lowlevel = True,)


for ti in range(1, 3):
    devices['ps%d_V' % ti] = device('nicos_mlz.kws1.devices.gedet.GEPowerSupply',
        description = 'detector power supply voltage',
        tangodevice = tango_base + 'gesupply/ps%d' % ti,
        unit = 'V',
        abslimits = (0, 54),
        userlimits = (0, 54),
        warnlimits = (53.9, 54.1),
        lowlevel = True,
    )
    devices['ps%d_I' % ti] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'detector power supply current',
        device = 'ps%d_V' % ti,
        parameter = 'current',
        unit = 'A',
        warnlimits = (2.4, 2.9),
        lowlevel = True,
    )

extended = dict(
    representative = 'gedet_HV',
)
