description = 'sample changer 2 devices'

group = 'optional'

includes = ['sample_changer', 'sample_table']

devices = dict(
    sc2 = device('nicos.devices.generic.MultiSwitcher',
        description = 'Sample Changer 2 Huber device',
        moveables = ['sc_y', 'st_z'],
        mapping = {
            1: [592.5, -32],
            2: [533.5, -32],
            3: [474.5, -32],
            4: [415.5, -32],
            5: [356.5, -32],
            6: [297.5, -32],
            7: [238.5, -32],
            8: [179.5, -32],
            9: [120.5, -32],
            10: [61.5, -32],
            11: [2.5, -32],
            12: [592.5, 27],
            13: [533.5, 27],
            14: [474.5, 27],
            15: [415.5, 27],
            16: [356.5, 27],
            17: [297.5, 27],
            18: [238.5, 27],
            19: [179.5, 27],
            20: [120.5, 27],
            21: [61.5, 27],
            22: [2.5, 27],
        },
        # changed by sbusch 2017-JUN-09 with tilted st1 (chi broken),
        # adjusted 4...7, 15...18
        # mapping = { 7: [360.6, -32.0],  6: [301.8, -32.0],
        #            5: [242.6, -31.9],  4: [183.6, -31.8],
        #           18: [358.2,  27.2], 17: [299.2,  27.2],
        #           16: [240.2,  27.1], 15: [181.1,  27.0],
        #           },
        fallback = 0,
        fmtstr = '%d',
        precision = [0.05, 0.05],
        # precision = [0.05, 0.05, 100], # for use without nicos
        blockingmove = False,
    ),
)

alias_config = {
    'SampleChanger': {'sc2': 100},
}
