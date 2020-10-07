description = 'ANDES setup'

group = 'basic'

# modules = []

includes = ['shutters', 'monochromator', 'sampletable', 'detector', 'detector_translation']

devices = dict(
    operationMode = device('nicos.devices.generic.MultiSwitcher',
        description = 'ANDES operation modes',
        moveables = ['crystal', 'mtt_opMode', 'lms_opMode', 'stt_opMode', 'lsd_opMode'],
        mapping = {
            'tension_scanner': ['BPC', 'min', 'min', 'ts', 'min'],
            'half_resolution': ['Ge', 'hf', 'min', 'min', 'lsd'],
            'high_intensity_Ge': ['Ge', 'min', 'min', 'min', 'lsd'],
            'high_intensity_PG': ['PG', 'hi2', 'min', 'min', 'lsd'],
        },
        precision = None,
    ),
)

startupcode = '''
printinfo("Welcome to ANDES.")
'''

