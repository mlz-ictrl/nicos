description = 'ANDES setup'

group = 'basic'

# modules = []

includes = ['shutters', 'monochromator', 'sampletable', 'detector']

devices = dict(
    operationMode = device('nicos.devices.generic.MultiSwitcher',
        description = 'ANDES operation modes',
        moveables = ['mtt_opMode', 'crystal', 'lms_opMode', 'stt_opMode', 'lsd_opMode'],
        mapping = {
            'tension_scanner': ['min', 'BPC', 'min', 'ts', 'min'],
            'half_resolution': ['hf', 'Ge', 'min', 'min', 'lsd'],
            'high_intensity_Ge': ['min', 'Ge', 'min', 'min', 'lsd'],
            'high_intensity_PG': ['hi2', 'PG', 'min', 'min', 'lsd'],
        },
        precision = None,
    ),
)

startupcode = '''
printinfo("Welcome to ANDES.")
'''

