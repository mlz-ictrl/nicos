description = 'Camini Camera Synchronisation Detector'

pvprefix = 'SQ:NEUTRA:CAMINI:'
pvprefix_sumi = 'SQ:NEUTRA:sumi:'
pvprefix_ai = 'SQ:NEUTRA:B5ADC:'

includes = ['shutters']

display_order = 70
epics_timeout = 3.0

devices = dict(
    cam_shut = device('nicos.devices.epics.EpicsReadable',
        epicstimeout = epics_timeout,
        description = 'Camera shutter open',
        readpv = pvprefix + 'SHUTTER',
        lowlevel = True,
    ),
    cam_arm = device('nicos.devices.epics.EpicsReadable',
        epicstimeout = epics_timeout,
        description = 'Camera ready for acquisition',
        readpv = pvprefix + 'ARM',
        lowlevel = True,
    ),
    cam_trig = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = epics_timeout,
        description = 'Camera trigger signal',
        readpv = pvprefix + 'TRIG',
        writepv = pvprefix + 'TRIG',
        lowlevel = True,
    ),
    cam_aux = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = epics_timeout,
        description = 'Exposure valid signal',
        readpv = pvprefix + 'AUX',
        writepv = pvprefix + 'AUX',
        lowlevel = True,
    ),
    cam_valid = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = epics_timeout,
        description = 'Metadata valid signal',
        readpv = pvprefix + 'VALID',
        writepv = pvprefix + 'VALID',
        lowlevel = True,
    ),
    camini = device('nicos_sinq.icon.devices.camini.CaminiDetector',
        epicstimeout = epics_timeout,
        description = 'Synchronization with the CAMINI camera '
        'software',
        trigpv = pvprefix + 'TRIG',
        validpv = pvprefix + 'VALID',
        metapv = pvprefix + 'META',
        shutpv = pvprefix + 'SHUTTER',
        armpv = pvprefix + 'ARM',
        filepv = pvprefix + 'FILE',
        shutter = 'exp_shutter',
        auto = 'exp_auto',
        beam_current = 'beam_current',
        rate_threshold = 'exp_threshold',
        arm_timeout = 5.0,
        shutter_timeout = 5.0,
        exposure_timeout = 300.0,
        lowlevel = True
    ),
    exp_threshold = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = 'Exposure threshold',
        readpv = pvprefix_sumi + 'THRES',
        writepv = pvprefix_sumi + 'THRES',
        abslimits = (-100, 2000),
        epicstimeout = epics_timeout
    ),
    exp_ok = device('nicos.devices.epics.EpicsReadable',
        description = 'Exposure sufficient',
        readpv = pvprefix + 'AUX',
        epicstimeout = epics_timeout
    ),
    exp_avg = device('nicos.devices.epics.EpicsReadable',
        description = 'Average exposure',
        readpv = pvprefix_sumi + 'BEAMAVG',
        epicstimeout = epics_timeout
    ),
    beam_current = device('nicos.devices.epics.EpicsReadable',
        description = 'Beam current',
        readpv = pvprefix_ai + 'V4',
        epicstimeout = epics_timeout
    ),
    exp_time = device('nicos.devices.epics.EpicsReadable',
        description = 'Exposure time',
        readpv = pvprefix_sumi + 'EXPTIME',
        epicstimeout = epics_timeout
    ),
    oracle = device('nicos_sinq.icon.devices.beamoracle.BeamOracle',
        description = 'Device to sum proton count',
        pvprefix = pvprefix_sumi,
        lowlevel = True,
        epicstimeout = epics_timeout
    ),
    camera = device('nicos_sinq.icon.devices.ccdcontrol.NIAGControl',
        description = 'Count control for NIAG CCD detectors',
        trigger = 'camini',
        followers = ['oracle'],
        rate_monitor = 'oracle',
        rate_threshold = 'exp_threshold',
        exp_ok = 'exp_ok',
    )
)
startupcode = '''
SetDetectors(camera)
'''
