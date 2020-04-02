description = 'Black detector box with fixed FOV'

group = 'basic'

includes = ['basic', 'sbl', 'huber', 'detector_translation', 'detector_ikonl',
            'detector_parameters']

excludes = []

startupcode = '''
move(camerabox, 'Black Box')
move(lens, 'Zeiss 100mm F2.0')
move(pixelsize, 67.0)
'''