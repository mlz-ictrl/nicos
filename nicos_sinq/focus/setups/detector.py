description = 'Devices for the Detector'

pvdprefix = 'SQ:FOCUS:counter'
devices = dict(
    timepreset = device('nicos_sinq.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = pvdprefix + '.TP',
        presetpv = pvdprefix + '.TP',
    ),
    elapsedtime = device('nicos_sinq.devices.epics.detector.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = pvdprefix + '.T',
    ),
    monitorpreset = device('nicos_sinq.devices.epics.detector.EpicsCounterActiveChannel',
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = pvdprefix + '.PR2',
        presetpv = pvdprefix + '.PR2',
    ),
    # The Primary Monitor Signal (CH1) is duplicated and sent to the position
    # encoder of the middle detectorbank (through the histogrammer to CH3).
    # There will always be periods of time where the Chopper is out of phase
    # (these periods aren't counted), so having both the primary and duplicated
    # signal (which passes through the detector box) we can more easily check
    # that the signal stayed in sync throughout a measurement by observing
    # whether the counts are equal.
    monitor1 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Primary Monitor Signal - just before the sample - (Counterbox CH1)',
        type = 'monitor',
        readpv = pvdprefix + '.S2',
    ),
    tof_sum = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Duplicated Monitor Signal - histogram sum - (CounterBox CH3)',
        type = 'monitor',
        readpv = pvdprefix + '.S4',
    ),
    beam_monitor = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Beam Monitor (Counterbox CH2)',
        type = 'monitor',
        readpv = pvdprefix + '.S3',
    ),
    protoncount = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Proton Count (Counterbox CH5)',
        type = 'monitor',
        readpv = pvdprefix + '.S6',
    ),
    # As all banks use the same time binning, this axis is shared
    hm_tof_array = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfTofArray',
        description = 'TOF Array for histogramming',
        tag = 'tof',
        dim = [
            5,
        ],
        data = [10, 20, 30, 40, 50],
        formatter = '%9d',
    ),
    middle_theta = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfArray',
        description = 'Middle bank two-theta',
        dim = [2],
        data = [0, 0],
        visibility = (),
        tag = 'mtheta'
    ),
    lower_theta = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfArray',
        description = 'lower bank two-theta',
        dim = [2],
        data = [0, 0],
        visibility = (),
        tag = 'ltheta'
    ),
    upper_theta = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfArray',
        description = 'Upper bank two-theta',
        dim = [2],
        data = [0, 0],
        visibility = (),
        tag = 'utheta'
    ),
    merged_theta = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfArray',
        description = 'Merged bank two-theta',
        dim = [2],
        data = [0, 0],
        visibility = (),
        tag = 'metheta'
    ),
    hm_ax_tof = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfAxis',
        description = 'TOF axis',
        mapping = 'boundary',
        array = 'hm_tof_array',
        label = 'TOF',
        visibility = (),
        unit = 'ms'
    ),
    delay = device('nicos.devices.generic.manual.ManualMove',
        description = 'A place to keep the delay value',
        abslimits = (0, 20000),
        unit = 'ms'
    ),
    merged_image = device('nicos_sinq.focus.devices.detector.MergedImageChannel',
        description = 'Image merged from middle, upper and lower banks',
        tof = 'hm_tof_array',
        mergefile = 'nicos_sinq/focus/focusmerge.dat'
    ),
    el737 = device('nicos_sinq.devices.detector.SinqDetector',
        description = 'EL737 counter box that counts neutrons and '
        'starts streaming events',
        startpv = pvdprefix + '.CNT',
        pausepv = pvdprefix + ':Pause',
        statuspv = pvdprefix + ':Status',
        errormsgpv = pvdprefix + ':MsgTxt',
        thresholdpv = pvdprefix + ':Threshold',
        thresholdcounterpv = pvdprefix + ':ThresholdCounter',
        monitorpreset = 'monitorpreset',
        timepreset = 'timepreset',
        timers = ['elapsedtime'],
        monitors = [
            'monitor1',
            'protoncount',
            'beam_monitor',
            'tof_sum',
        ],
        images = [
            'merged_image',
        ],
        liveinterval = 7,
        saveintervals = [60]
    ),
    focusdet = device('nicos_sinq.focus.devices.detector.FocusDetector',
        description = 'FOCUS detector control',
        trigger = 'el737',
        followers = [],
        liveinterval = 120,
        saveintervals = [0, 900, 900],
    ),
    em_td = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Emmenegger time delay',
        readpv = 'SQ:FOCUS:EMMI:TD_RBV',
        writepv = 'SQ:FOCUS:EMMI:TD',
        precision = 10,
        abslimits = (0, 200000)
    ),
    em_aw = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Emmenegger acceptance window',
        readpv = 'SQ:FOCUS:EMMI:AW_RBV',
        writepv = 'SQ:FOCUS:EMMI:AW',
        precision = 5,
        abslimits = (0, 20000)
    ),
)
startupcode = """
LoadThetaArrays()
SetDetectors(focusdet)
"""
