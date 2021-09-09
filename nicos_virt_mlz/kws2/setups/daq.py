# -*- coding: utf-8 -*-

description = 'Detector data acquisition setup'
group = 'lowlevel'
display_order = 25

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat', 'binaryformat', 'LiveViewSink'],
)

devices = dict(
    mcstas = device('nicos_virt_mlz.kws2.devices.mcstas.KwsSimulation',
        description = 'McStas simulation',
        mcstasprog = 'KWS2pra -g',
        neutronspersec = 4e5,
        intensityfactor = 1,
    ),
    det_ext_rt = device('nicos.devices.generic.ManualSwitch',
        description = 'Switch for external-start realtime mode',
        lowlevel = True,
        states = ['on', 'off', 1, 0],
    ),
    det_img = device('nicos_virt_mlz.kws2.devices.mcstas.KwsDetectorImage',
        description = 'Detector image',
        mcstas = 'mcstas',
        size = (144, 256),
        mcstasfile = 'PSD_scattering.psd',
        fmtstr = '%d',
        unit = 'cts',
        lowlevel = True,
    ),
    det_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Current detector mode',
        device = 'det_img',
        parameter = 'mode',
    ),
    timer = device('nicos.devices.mcstas.McStasTimer',
        description = 'timer',
        mcstas = 'mcstas',
        fmtstr = '%.0f',
    ),
    mon1 = device('nicos.devices.mcstas.McStasCounter',
        description = 'Monitor 1 (before selector)',
        type = 'monitor',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_mon1.psd',
        fmtstr = '%d',
    ),
    mon2 = device('nicos.devices.mcstas.McStasCounter',
        description = 'Monitor 2 (after selector)',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_mon2.psd',
        type = 'monitor',
        fmtstr = '%d',
    ),
    # mon3 = device('nicos.devices.generic.VirtualCounter',
    #     description = 'Monitor 3 (in detector beamstop)',
    #     type = 'monitor',
    #     fmtstr = '%d',
    # ),
    kwsformat = device('nicos_mlz.kws1.devices.kwsfileformat.KWSFileSink',
        transpose = False,
        detectors = ['det'],
    ),
    yamlformat = device('nicos_mlz.kws1.devices.yamlformat.YAMLFileSink',
        detectors = ['det'],
    ),
    binaryformat = device('nicos_mlz.kws1.devices.yamlformat.BinaryArraySink',
        detectors = ['det'],
    ),
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    det = device('nicos_mlz.kws1.devices.daq.KWSDetector',
        description = 'KWS detector',
        liveinterval = None,
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        images = ['det_img'],
        others = [],
        shutter = 'shutter',
    ),
)

startupcode = '''
SetDetectors(det)
'''

extended = dict(
    poller_cache_reader = ['shutter'],
    representative = 'det_img',
)
