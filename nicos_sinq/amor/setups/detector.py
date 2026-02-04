description = 'Multiblade detector'

display_order = 15

sysconfig = dict(datasinks = ['jbi_liveview', 'FileWriterControl'],)

includes = ['chopper_sim']

sumpv = 'SQ:AMOR:sumi:'

devices = dict(
    det_timer = device('nicos.devices.generic.VirtualTimer',
                       description = 'Detector timer',
                       fmtstr = '%7.1f',
                       unit = 's',
                       ),
    #det_image = device('nicos_sinq.devices.just_bin_it.JustBinItImage',
    #                   description = 'Detector image channel',
    #                   hist_topic = 'AMOR_histograms',
    #                   data_topic = 'amor_ev44',
    #                   command_topic = 'AMOR_histCommands',
    #                   brokers = configdata('config.KAFKA_BROKERS'),
    #                   unit = 'evts',
    #                   hist_type = '2-D DET',
    #                   det_width = 32,
    #                   det_height = 448,
    #                   det_range = (0, 32*448),
    #                   pollinterval = 0.5,
    #                   visibility = ('metadata', 'namespace'),
    #                   ),
    hist_yz = device('nicos_sinq.devices.just_bin_it.JustBinItImage',
                     description = 'Detector pixel histogram over all times',
                     hist_topic = 'AMOR_histograms_YZ',
                     data_topic = 'amor_ev44',
                     command_topic = 'AMOR_histCommands',
                     brokers = configdata('config.KAFKA_BROKERS'),
                     unit = 'evts',
                     hist_type = '2-D SANSLLB',
                     det_width = 446,
                     det_height = 64,
                     visibility = ('metadata', 'namespace'),
                     ),
    hist_tofz = device('nicos_sinq.devices.just_bin_it.JustBinItImage',
                       description = 'Detector time of flight vs. z-pixel histogram over all y-values',
                       hist_topic = 'AMOR_histograms_TofZ',
                       data_topic = 'amor_ev44',
                       command_topic = 'AMOR_histCommands',
                       brokers = configdata('config.KAFKA_BROKERS'),
                       unit = 'evts',
                       hist_type = '2-D SANSLLB',
                       det_width = 118,
                       det_height = 446,
                       visibility = ('metadata', 'namespace'),
                       ),
    roi1 = device('nicos_sinq.amor.devices.roi_tmp.CutROI',
                  description = "ROI 1",
	              raw_image = 'hist_yz',
                  roi = (0, 200, 64, 46),
                  fmtstr = '%d cts (%.1f cpm)',
	              ),
    det = device('nicos.devices.generic.Detector',
                 description = 'The just-bin-it histogrammer',
                 unit = '',
                 timers = ['det_timer'],
                 #monitors = ['beam_monitor', 'proton_monitor'],
                 monitors = ['proton_monitor'],
                 images = ['hist_yz', 'hist_tofz'],
                 liveinterval=5.0,
                 counters = ['roi1'],
	         #postprocess = [("roi1", "hist_yz", "proton_monitor"),], # for future with default ROI implementation
                 visibility = ('metadata', 'namespace'),
                 ),
    proton_monitor = device('nicos_sinq.devices.epics.proton_counter.SINQProtonMonitor',
                            description = 'Proton monitor',
                            pvprefix = sumpv,
                            fmtstr = '%.1e',
                            unit = 'mC',
                            type = 'monitor',
                            ),
    detector_rate = device('nicos_sinq.amor.devices.detector.DetectorRate',
                           description = 'Status of the file-writer',
                           brokers = configdata('config.KAFKA_BROKERS'),
                           topic = configdata('config.DETECTOR_EVENTS_TOPIC'),
                           chopper_speed = 'ch1_speed',
                           unit = '/s',
                           ),

    jbi_liveview = device('nicos.devices.datasinks.LiveViewSink'),
    synchronize_daq = device('nicos_sinq.amor.devices.datasinks.SyncDaqSink'),
    )

startupcode = '''
SetDetectors(det)
'''
