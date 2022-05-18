description = 'alias for detector'

group = 'lowlevel'

devices = dict(
    det1 = device('nicos.devices.generic.DeviceAlias',
        devclass='nicos_mlz.sans1.devices.detector.Detector',
    ),
)
