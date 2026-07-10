description = 'Andor Neo sCMOS camera emulation'
group = 'lowlevel'

devices = dict(
    timer_neo = device('nicos.devices.generic.VirtualTimer',
        description = 'The camera\'s internal timer',
        visibility = (),
    ),
    neo = device('nicos_virt_mlz.antares.devices.camera.Camera',
        description = 'Andor Neo sCMOS camera detector image',
        cameramodel = 'Neo',
        fmtstr = '%d',
        hwsize = (2560, 2160),
        bin = (2, 2),
        visibility = (),
    ),
    temp_neo = device('nicos.devices.generic.VirtualTemperature',
        description = 'The CMOS chip temperature',
        abslimits = (-100, 0),
        warnlimits = (None, 0),
        speed = 6,
        unit = 'degC',
        maxage = 5,
        fmtstr = '%.0f',
    ),
    det_neo = device('nicos.devices.generic.Detector',
        description = 'The Andor Neo sCMOS camera detector',
        images = ['neo'],
        timers = ['timer_neo'],
    ),
)

startupcode = """
SetDetectors(det_neo)
"""
