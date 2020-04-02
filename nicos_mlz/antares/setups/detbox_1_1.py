description = 'High Resolution Detector Box in 1:1 configuration'

group = 'basic'

includes = ['basic', 'sbl', 'huber', 'detector_translation', 'detector_neo',
            'detector_parameters','scintillatortx']

excludes = ['tmp_detbox_1_4', 'tmp_detbox_1_8']

startupcode = '''
scintillatortx.usermin = 175
neo.rotation = 90
neo.flip = (False, True)
move(camerabox, 'Neo Box 2019 - 1 mirror config 1:1')
move(lens, 'Leica 100mm with macro adapter')
'''