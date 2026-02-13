description = 'Devices for the DAQ/Counterbox a Narziss'
group = 'lowlevel'

pvdprefix = 'SQ:NARZISS:DAQ'

channels = [ 'mon1', 'ctr1', 'c3', 'protoncount', 'c5', 'c6', 'c7', 'c8' ] 

devices = dict(
    elapsedtime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = pvdprefix,
    ),
    DAQPreset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = '2nd Generation Data Acquisition',
        daqpvprefix = pvdprefix,
        channels = channels,
        time_channel = ['elapsedtime'],
    ),
    ThresholdChannel = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThresholdChannel',
        daqpvprefix = pvdprefix,
        channels = channels,
    ),
    Threshold = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThreshold',
        daqpvprefix = pvdprefix,
        min_rate_channel = 'ThresholdChannel',
    ),
    mon1 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'First monitor',
        daqpvprefix = pvdprefix,
        channel = 1,
        type = 'monitor',
    ),
    ctr1 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Second monitor',
        daqpvprefix = pvdprefix,
        channel = 2,
        type = 'monitor',
    ),
    mon2 = device(
        'nicos.core.device.DeviceAlias',
        alias = 'ctr1',
        ),
    c3 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Third input',
        daqpvprefix = pvdprefix,
        channel = 3,
        type = 'monitor',
    ),
    protoncount = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor for proton current',
        daqpvprefix = pvdprefix,
        channel = 4,
        type = 'monitor',
    ),
    c5 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Third input',
        daqpvprefix = pvdprefix,
        channel = 5,
        type = 'monitor',
    ),
    c6 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Third input',
        daqpvprefix = pvdprefix,
        channel = 6,
        type = 'monitor',
    ),
    c7 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Third input',
        daqpvprefix = pvdprefix,
        channel = 7,
        type = 'monitor',
    ),
    c8 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Third input',
        daqpvprefix = pvdprefix,
        channel = 8,
        type = 'monitor',
    ),
    narzissdet = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'EL737 counter box that counts neutrons and starts streaming events',
        timers = ['elapsedtime'],
        monitors = ['DAQPreset'] + channels,
        counters = [],
        liveinterval = 7,
        saveintervals = [60]
    ),
)

startupcode = """
SetDetectors(narzissdet)
"""
