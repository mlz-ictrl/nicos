description = 'Frappy demo in NICOS!'

group = 'plugplay'

devices = dict(
    barcode_frappy = device(
        'nicos.devices.secop.SecNodeDevice',
        prefix = 'frappy_',
        description='frappy demo',
        uri = 'tcp://localhost:10767',
        auto_create=True,
        unit='',
        device_mapping = {
            'barcodes': {
                'name': 'barcode',
                'mixins': [
                    'nicos_mlz.devices.barcodes.BarcodeInterpreterMixin',
                ],
                'parameters': {
                    'commandmap': {},
                },
            },
        },
    ),
)
