description = 'Setup for the beam monitoring devices'

pvprefix_sumi = 'SQ:ICON:sumi:'
pvprefix_ai = 'SQ:ICON:B5ADC:'

devices = dict(
    exp_threshold = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Exposure threshold',
        readpv = pvprefix_sumi + 'THRES',
        writepv = pvprefix_sumi + 'THRES',
        precision = 10,
        abslimits = (-100, 2000),
    ),
    exp_avg = device('nicos_sinq.icon.devices.epics_devices.EpicsReadable',
        description = 'Average exposure',
        readpv = pvprefix_sumi + 'BEAMAVG',
    ),
    beam_current = device('nicos_sinq.icon.devices.epics_devices.EpicsReadable',
        description = 'Beam current',
        readpv = pvprefix_ai + 'V4',
    ),
    exp_time = device('nicos_sinq.icon.devices.epics_devices.EpicsReadable',
        description = 'Exposure time',
        readpv = pvprefix_sumi + 'EXPTIME',
    ),
    oracle = device('nicos_sinq.devices.beamoracle.BeamOracle',
        description = 'Device to sum proton count',
        pvprefix = pvprefix_sumi,
        visibility = (),
    ),
)
