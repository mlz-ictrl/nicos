description = 'devices for fast detector using comtec p7888 for REFSANS'

# to be included by refsans?
group = 'optional'

excludes = ['detector']

sysconfig = dict(
    datasinks = ['RawFileSaver'],
)

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test/fast' % nethost

devices = dict(
    RawFileSaver = device('nicos.devices.datasinks.SingleRawImageSink',
        description = 'Saves image data in RAW format',
        filenametemplate = [
            '%(proposal)s_%(pointcounter)s.raw', '%(proposal)s_%(scancounter)s'
            '_%(pointcounter)s_%(pointnumber)s.raw'
        ],
        lowlevel = True,
    ),
    fastctr_a = device('nicos.devices.taco.detector.FRMCounterChannel',
        description = "Channel A of Comtep P7888 Fast Counter",
        tacodevice = '%s/rate_a' % tacodev,
        type = 'counter',
        mode = 'normal',
    ),
    fastctr_b = device('nicos.devices.taco.detector.FRMCounterChannel',
        description = "Channel B of Comtep P7888 Fast Counter",
        tacodevice = '%s/rate_b' % tacodev,
        type = 'counter',
        mode = 'normal',
    ),
    fastctr_c = device('nicos.devices.taco.detector.FRMCounterChannel',
        description = "Channel C of Comtep P7888 Fast Counter",
        tacodevice = '%s/rate_c' % tacodev,
        type = 'counter',
        mode = 'normal',
    ),
    fastctr_d = device('nicos.devices.taco.detector.FRMCounterChannel',
        description = "Channel D of Comtep P7888 Fast Counter",
        tacodevice = '%s/rate_d' % tacodev,
        type = 'counter',
        mode = 'normal',
    ),
    fastctr_e = device('nicos.devices.taco.detector.FRMCounterChannel',
        description = "Channel E of Comtep P7888 Fast Counter",
        tacodevice = '%s/rate_e' % tacodev,
        type = 'counter',
        mode = 'normal',
    ),
    fastctr_f = device('nicos.devices.taco.detector.FRMCounterChannel',
        description = "Channel F of Comtep P7888 Fast Counter",
        tacodevice = '%s/rate_f' % tacodev,
        type = 'counter',
        mode = 'normal',
    ),
    fastctr_g = device('nicos.devices.taco.detector.FRMCounterChannel',
        description = "Channel G of Comtep P7888 Fast Counter",
        tacodevice = '%s/rate_g' % tacodev,
        type = 'counter',
        mode = 'normal',
    ),
    fastctr_h = device('nicos.devices.taco.detector.FRMCounterChannel',
        description = "Channel H of Comtep P7888 Fast Counter",
        tacodevice = '%s/rate_h' % tacodev,
        type = 'counter',
        mode = 'normal',
    ),
    # the following may not work as expected ! (or at all!)
    # comtec = device('nicos.devices.vendor.qmesydaq.QMesyDAQImage',
    #     description = 'Comtep P7888 Fast Counter Main detector device',
    #     tacodevice = '%s/detector' % tacodev,
    #     events = None,
    #     timer = None,
    #     counters = ['fastctr_a','fastctr_b','fastctr_c','fastctr_d',
    #     'fastctr_e','fastctr_f','fastctr_g','fastctr_h'],
    #     monitors = None,
    #     fileformats = ['RawFileSaver'],
    #     subdir = 'fast',
    # ),
)

startupcode = """
# SetDetectors(comtec)
"""
