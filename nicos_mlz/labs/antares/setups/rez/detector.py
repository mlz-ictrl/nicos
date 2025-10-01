description = 'External Detector triggered by file'

group = 'optional'

excludes = []

devices = dict(
#    timer = device('nicos_mlz.antares.devices.TriggerTimerStatusFile',
#        description = 'Software timer',
#        filepath = '/home/localadmin/trigger_rez_detector/Data/Test001.txt',
#    ),
    timer = device('nicos.devices.entangle.TimerChannel',
        description = 'Software timer that creates a file on start and waits for the file to be deleted to stop.',
        tangodevice = 'tango://localhost:10000/hk6/detector/timer',
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Detector',
        timers = ['timer'],
    ),
)

startup_code = """
SetDetectors(det)
"""
