description = 'Setup for the new collimator (2020) controlled through a SPSS7 and EPICS'

pvprefix = 'SQ:SANS'

excludes = ['collimator', 'polariser']

segments = {
    'cols1': ':colS1',
    'cols2': ':colS2',
    'cols3': ':colS3',
    'cols4': ':colS4',
    'cols5': ':colS5',
    'cols6': ':colS6',
    'cols7': ':colS7'
}

segwrite = {'hand': ':HAND', 'ble': ':BLE', 'nl': ':NL', 'zus': ':ZUS'}

segread = [
    'mot_slow', 'mot_fast', 'lbol_lock', 'lbol_unlock', 'rbol_lock',
    'rbol_unlock', 'mot_error', 'seq_error', 'bol_error'
]

hide = True

devices = dict()

for col, colpv in segments.items():
    for name, itempv in segwrite.items():
        devices[col + '_io' + name] = device('nicos_sinq.sans.devices.collimator.SegmentMoveable',
            description = '%s %s switch device' % (col, name),
            lowlevel = hide,
            writepv = pvprefix + colpv + itempv,
            readpv = pvprefix + colpv + itempv + '_RBV',
            epicstimeout = 3.0
        )
        devices[col + '_' + name] = device('nicos_sinq.sans.devices.collimator.SegmentPulse',
            description = '%s %s pulse device' % (col, name),
            moveable = col + '_io' + name,
            onvalue = 1,
            offvalue = 0,
            lowlevel = hide,
            ontime = 1.5
        )
    for name in segread:
        devices[col + '_' + name] = device('nicos.devices.epics.EpicsReadable',
            description = '%s %s readout' % (col, name),
            lowlevel = hide,
            readpv = pvprefix + colpv + ':' + name.upper() + '_RBV',
            epicstimeout = 3.0
        )
    devices[col] = device('nicos_sinq.sans.devices.collimator.Segment',
        description = 'Collimator segment %s' % col,
        hand = col + '_hand',
        ble = col + '_ble',
        nl = col + '_nl',
        zus = col + '_zus',
        mot_error = col + '_mot_error',
        seq_error = col + '_seq_error',
        bolt_error = col + '_bol_error',
        mot_fast = col + '_mot_fast',
        mot_slow = col + '_mot_slow',
    )

devices['pol'] = device('nicos_sinq.sans.devices.collimator.Polariser',
    description = 'Switch for polariser',
    cols1 = 'cols1'
)
devices['coll'] = device('nicos_sinq.sans.devices.collimator.Collimator',
    description = 'Collimator length control',
    segments = list(segments.keys()),
    unit = 'm',
)
