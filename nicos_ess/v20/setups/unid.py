description = 'uNID Detector Integration'

devices = dict(
    unid = device(
        'nicos_ess.v20.devices.unid.uNIDController',
        urlbase='http://192.168.1.148/daqmw/scripts',
        description='uNID Controller',
        maxage=0.5,
    ),
)
