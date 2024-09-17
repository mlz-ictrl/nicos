description = 'Loads all the devices of the collimator'

includes = ['mcu2', 'rack09', 'rack11', 'rack12']

devices = dict(
    coll = device('nicos.devices.generic.MultiSwitcher',
        description = 'Collimator selector',
        moveables = ['pol', 'guide1', 'guide2', 'guide3', 'guide4', 'guide5'],
        mapping = {
            '1250': ['in', 'in', 'in', 'in', 'in', 'in'],
            '3000': ['in', 'in', 'in', 'in', 'in', 'out'],
            '4250': ['in', 'in', 'in', 'in', 'out', 'out'],
            '8000': ['in', 'in', 'in', 'out', 'out', 'out'],
            '11750': ['in', 'in', 'out', 'out', 'out', 'out'],
            '15500': ['in', 'out', 'out', 'out', 'out', 'out'],
            '18500': ['out', 'out', 'out', 'out', 'out', 'out'],
        },
        precision = [None],
    ),
)
