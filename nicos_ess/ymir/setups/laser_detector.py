description = 'The laser detector in the YMIR cave'

devices = dict(
    laser=device('nicos_ess.ymir.devices.laser_detector.LaserDetector',
                 description='Laser detector in YMIR cave',),
)
