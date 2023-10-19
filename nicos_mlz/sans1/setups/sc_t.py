description = 'sample changer temperature device'

group = 'optional'

includes = ['sample_changer', 'sample_table']

devices = dict(
    sc_t = device('nicos.devices.generic.MultiSwitcher',
        description = 'Sample Changer temperature Huber device',
        moveables = ['sc_y', 'st_z'],
        mapping = {
            11: [592.50, -3.6],
            10: [533.50, -3.0],
            9: [475.00, -3.0],
            8: [417.00, -3.0],
            7: [356.75, -3.0],
            6: [298.50, -3.0],
            5: [240.00, -3.0],
            4: [179.50, -3.0],
            3: [121.50, -3.0],
            2: [64.00, -3.0],
        },
        fallback = 0,
        fmtstr = '%d',
        precision = [0.05, 0.05],
        # precision = [0.05, 0.05, 100], # for use without nicos
        blockingmove = False,
    ),
)

alias_config = {
    'SampleChanger': {'sc_t': 100},
}
