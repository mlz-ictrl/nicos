#  -*- coding: utf-8 -*-

description = 'common detector devices provided by QMesyDAQ'

group = 'lowlevel'

tango_base = 'tango://mesydaq.puma.frm2.tum.de:10000/qm/qmesydaq/'

devices = dict(
    timer = device('nicos.devices.entangle.TimerChannel',
        description = 'QMesyDAQ timer',
        tangodevice = tango_base + 'timer',
        lowlevel = True,
    ),
    mon1 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ monitor 1',
        tangodevice = tango_base + 'counter0',
        type = 'monitor',
        lowlevel = True,
        fmtstr = '%d',
    ),
    # mon2 = device('nicos.devices.entangle.CounterChannel',
    #     tangodevice = tango_base + 'a2',
    #     type = 'monitor',
    #     lowlevel = True,
    #     fmtstr = '%d',
    # ),
    det1 = device('nicos.devices.entangle.CounterChannel',
        tangodevice = tango_base + 'counter1',
        type = 'counter',
        lowlevel = True,
        fmtstr = '%d',
    ),
    det2 = device('nicos.devices.entangle.CounterChannel',
        tangodevice = tango_base + 'counter2',
        type = 'counter',
        lowlevel = True,
        fmtstr = '%d',
    ),
    det3 = device('nicos.devices.entangle.CounterChannel',
        tangodevice = tango_base + 'counter3',
        type = 'counter',
        lowlevel = True,
        fmtstr = '%d',
    ),
    # det4 = device('nicos.devices.entangle.CounterChannel',
    #     tangodevice = tango_base + 'b2',
    #     type = 'counter',
    #     lowlevel = True,
    #     fmtstr = '%d',
    # ),
    # det5 = device('nicos.devices.entangle.CounterChannel',
    #     tangodevice = tango_base + 'b3',
    #     type = 'counter',
    #     lowlevel = True,
    #     fmtstr = '%d',
    # ),
    events = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Events channel',
        tangodevice = tango_base + 'events',
        type = 'counter',
        lowlevel = True,
        fmtstr = '%d',
    ),
    image = device('nicos.devices.vendor.qmesydaq.tango.ImageChannel',
        description = 'QMesyDAQ Image',
        tangodevice = tango_base + 'image',
        lowlevel = True,
    ),
)

startupcode = '''
SetDetectors(det)
'''
