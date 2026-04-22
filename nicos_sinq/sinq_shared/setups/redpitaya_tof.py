description = 'RedPitaya TOF Detector'

group = 'lowlevel'

sysconfig = dict(datasinks = ['livesink'])

devices = dict(
    livesink = device('nicos_sinq.sinq_shared.datasinks.RedPitaya_livesinks.TofLiveViewSink',
        description = "Live view for RedPitaya TOF histograms"
    ),

    # HTTP Connector — shared by all RedPitaya TOF devices
    redpitaya_connector = device('nicos_sinq.devices.sinqhm.connector.HttpConnector',
        description = 'HTTP connector to RedPitaya Webserver',
        baseurl = 'http://rp-f0d629:8080',
        base64auth = '',
        byteorder = 'little',
    ),

    # RedPitaya TOF Controller
    redpitaya_daq_controller = device('nicos_sinq.sinq_shared.devices.RedPitayaTOF.TofDaqController',
        description = 'RedPitaya DAQ Start/Stop Controller',
        connector = 'redpitaya_connector',
    ),

    # Histogram Channels — one per channel and histogramtype
    ttl_ch0_tof = device('nicos_sinq.sinq_shared.devices.RedPitayaTOF.TofTOFChannel',
        description = 'TTL channel 0 — TOF Histogramm',
        channel = 'ttl_ch0',
        histtype = 'tof',
        pollinterval = 5,
        connector = 'redpitaya_connector',
    ),

    analog_ch0_tof = device('nicos_sinq.sinq_shared.devices.RedPitayaTOF.TofTOFChannel',
        description = 'Analog channel 0 — TOF Histogramm',
        channel = 'analog_ch0',
        histtype = 'tof',
        connector = 'redpitaya_connector',
    ),

    analog_ch0_ph = device('nicos_sinq.sinq_shared.devices.RedPitayaTOF.TofPulseheightChannel',
        description = 'Analog channel 0 — Pulseheight Histogramm',
        channel = 'analog_ch0',
        histtype = 'pulseheight',
        connector = 'redpitaya_connector',
    ),

    analog_ch1_tof = device('nicos_sinq.sinq_shared.devices.RedPitayaTOF.TofTOFChannel',
        description = 'Analog channel 1 — TOF Histogramm',
        channel = 'analog_ch1',
        histtype = 'tof',
        connector = 'redpitaya_connector',
    ),

    analog_ch1_ph = device('nicos_sinq.sinq_shared.devices.RedPitayaTOF.TofPulseheightChannel',
        description = 'Analog channel 1 — Pulseheight Histogramm',
        channel = 'analog_ch1',
        histtype = 'pulseheight',
        connector = 'redpitaya_connector',
    ),

    # Distance to chopper
    chopper_to_detector_distance = device('nicos.devices.generic.ManualMove',
        description = 'Sample to detector distance',
        unit = 'mm',
        abslimits = (0, 100000),
        default = 0,
    ),
)

startupcode = '''
'''
