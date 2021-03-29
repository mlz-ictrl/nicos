# -*- coding: utf-8 -*-
description = 'Detector test table setup'

group = 'basic'
excludes = ['det', 'ndp']
includes = ['treff', 'counter']

sysconfig = dict(
    datasinks = ['LiveViewSink', 'NPFileSink'],
)

tango_base = 'tango://phys.treff.frm2:10000/treff/'

devices = dict(
    # table axes on Phytron controller
    det_ax = device('nicos.devices.tango.Motor',
        description = 'table X (horizontal) axis',
        tangodevice = tango_base + 'phytron/ax',
        fmtstr = '%.2f',
    ),
    det_ay = device('nicos.devices.tango.Motor',
        description = 'table Y (vertical) axis',
        tangodevice = tango_base + 'phytron/ay',
        fmtstr = '%.2f',
    ),

    # Iseg HV supply
    det_HV1 = device('nicos.devices.tango.PowerSupply',
        description = 'first channel of HV supply',
        tangodevice = tango_base + 'iseghv/ch1',
        pollinterval = 20,
        maxage = 45,
        fmtstr = '%.0f',
    ),
    det_HV2 = device('nicos.devices.tango.PowerSupply',
        description = 'second channel of HV supply',
        tangodevice = tango_base + 'iseghv/ch2',
        pollinterval = 20,
        maxage = 45,
        fmtstr = '%.0f',
    ),

    # MCA detector readout
    det_mca_spectrum = device('nicos_mlz.treff.devices.roichan.SumImageChannel',
        description = '8k channel CAEN MCA',
        tangodevice = tango_base + 'caen/mca',
    ),
    det_mca_roi = device('nicos_mlz.treff.devices.roichan.LinearROIChannel',
        description = 'integrated counts in ROI',
    ),
    det_mca_timer = device('nicos.devices.tango.TimerChannel',
        description = 'timer for CAEN MCA',
        tangodevice = tango_base + 'caen/timer',
    ),
    det_mca = device('nicos.devices.generic.Detector',
        description = 'detector device with CAEN MCA',
        timers = ['timer', 'det_mca_timer'],
        counters = ['det_mca_roi'],
        images = ['det_mca_spectrum'],
        monitors = ["mon0", "mon1"],
        postprocess = [
            ('det_mca_roi', 'det_mca_spectrum'),
        ],
    ),

    LiveViewSink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sends spectrum data to LiveViewWidget',
    ),
    NPFileSink = device('nicos.devices.datasinks.text.NPFileSink',
        description = 'Saves spectrum as a simple text file',
    ),
)
