description = 'High Resolution Detector Box in 1:4 configuration'

group = 'basic'

includes = ['basic', 'sbl', 'huber', 'detector_translation', 'detector_neo',
            'detector_parameters','scintillatortx']

excludes = ['tmp_detbox_1_1', 'tmp_detbox_1_4']

startupcode = '''
scintillatortx.usermin = 0
scintillatortx.usermax = 200
neo.rotation = 270
neo.flip = (False, False)
move(camerabox, 'Neo Box 2019 - 2 mirror config 1:8')
move(lens, 'Zeiss 100mm F2.0')
'''