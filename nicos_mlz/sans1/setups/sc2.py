description = 'sample changer 2 devices'

group = 'optional'

includes = ['sample_changer', 'sample_table_1']

tango_host = 'tango://sans1hw.sans1.frm2:10000/sans1/sample_changer/'

devices = dict(
    sc2_y = device('nicos.devices.generic.Axis',
        description = 'Sample Changer 1/2 Axis',
        pollinterval = 15,
        maxage = 60,
        fmtstr = '%.2f',
        abslimits = (-0, 600),
        precision = 0.01,
        motor = 'sc2_ymot',
        coder = 'sc2_yenc',
        obs = [],
    ),
    sc2_ymot = device('nicos.devices.tango.Motor',
        description = 'Sample Changer 1/2 Axis motor',
        tangodevice = tango_host + 'y_mot',
        fmtstr = '%.2f',
        abslimits = (-0, 600),
        lowlevel = True,
    ),
    sc2_yenc = device('nicos.devices.tango.Sensor',
        description = 'Sample Changer 1/2 Axis encoder',
        tangodevice = tango_host + 'y_enc',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    sc2 = device('nicos.devices.generic.MultiSwitcher',
        description = 'Sample Changer 2 Huber device',
        moveables = ['sc2_y', 'st1_z'],
        mapping = {
            11: [592.5, -32],
            10: [533.5, -32],
            9: [474.5, -32],
            8: [415.5, -32],
            7: [356.5, -32],
            6: [297.5, -32],
            5: [238.5, -32],
            4: [179.5, -32],
            3: [120.5, -32],
            2: [61.5, -32],
            1: [2.5, -32],
            22: [592.5, 27],
            21: [533.5, 27],
            20: [474.5, 27],
            19: [415.5, 27],
            18: [356.5, 27],
            17: [297.5, 27],
            16: [238.5, 27],
            15: [179.5, 27],
            14: [120.5, 27],
            13: [61.5, 27],
            12: [2.5, 27],
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
        lowlevel = False,
    ),
)

alias_config = {
    'SampleChanger': {'sc2': 100},
}
