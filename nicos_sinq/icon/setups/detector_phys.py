description = 'Physical Camera Synchronisation'

pvprefix = 'SQ:ICON:CPHYS:'
pvprefix_dummy = 'SQ:ICON:CAMDUMMY:'
pvprefix_sumi = 'SQ:ICON:sumi:'
pvprefix_ai = 'SQ:ICON:B5ADC:'

includes = ['shutters']
excludes = ['detector']

display_order = 90

devices = dict(
    cam_shut = device('nicos.devices.epics.EpicsReadable',
        description = 'Camera shutter open',
        readpv = pvprefix + 'SHUTTER',
        lowlevel = True,
    ),
    cam_arm = device('nicos.devices.epics.EpicsReadable',
        description = 'Camera ready for acquisition',
        readpv = pvprefix + 'ARM',
        lowlevel = True,
    ),
    cam_trig = device('nicos.devices.epics.EpicsDigitalMoveable',
        description = 'Camera trigger signal',
        readpv = pvprefix + 'TRIG',
        writepv = pvprefix + 'TRIG',
        lowlevel = True,
    ),
    camini = device('nicos_sinq.devices.camini.CaminiDetector',
        description = 'Synchronization with the camera using physical signals',
        trigpv = pvprefix + 'TRIG',
        validpv = pvprefix_dummy + 'VALID',
        metapv = pvprefix_dummy + 'META',
        shutpv = pvprefix + 'SHUTTER',
        armpv = pvprefix + 'ARM',
        filepv = pvprefix_dummy + 'FILE',
        shutter = 'exp_shutter',
        auto = 'exp_auto',
        beam_current = 'beam_current',
        rate_threshold = 'exp_threshold',
        arm_timeout = 5.0,
        shutter_timeout = 5.0,
        exposure_timeout = 300.0,
        lowlevel = False
    ),
    exp_threshold = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = 'Exposure threshold',
        readpv = pvprefix_sumi + 'THRES',
        writepv = pvprefix_sumi + 'THRES',
        abslimits = (-100, 2000),
    ),
    exp_ok = device('nicos.devices.epics.EpicsReadable',
        description = 'Exposure sufficient',
        readpv = pvprefix + 'AUX',
    ),
    exp_avg = device('nicos.devices.epics.EpicsReadable',
        description = 'Average exposure',
        readpv = pvprefix_sumi + 'BEAMAVG',
    ),
    beam_current = device('nicos.devices.epics.EpicsReadable',
        description = 'Beam current',
        readpv = pvprefix_ai + 'V4',
    ),
    exp_time = device('nicos.devices.epics.EpicsReadable',
        description = 'Exposure time',
        readpv = pvprefix_sumi + 'EXPTIME',
    ),
    oracle = device('nicos_sinq.devices.beamoracle.BeamOracle',
        description = 'Device to sum proton count',
        pvprefix = pvprefix_sumi,
        lowlevel = True,
    ),
    camera = device('nicos_sinq.devices.ccdcontrol.NIAGControl',
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
