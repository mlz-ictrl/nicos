description = 'sample changer temperature device'

group = 'optional'

includes = ['sample_changer', 'sample_table_1']

tango_host = 'tango://sans1hw.sans1.frm2:10000/sans1/sample_changer/'

devices = dict(
    sc_t_y = device('nicos.devices.generic.Axis',
        description = 'Sample Changer 1/2/t Axis',
        pollinterval = 15,
        maxage = 60,
        fmtstr = '%.2f',
        abslimits = (-0, 600),
        precision = 0.01,
        motor = 'sc_t_ymot',
        coder = 'sc_t_yenc',
        obs = [],
    ),
    sc_t_ymot = device('nicos.devices.tango.Motor',
        description = 'Sample Changer 1/2/t Axis motor',
        tangodevice = tango_host + 'y_mot',
        fmtstr = '%.2f',
        abslimits = (-0, 600),
        lowlevel = True,
    ),
    sc_t_yenc = device('nicos.devices.tango.Sensor',
        description = 'Sample Changer 1/2/t Axis encoder',
        tangodevice = tango_host + 'y_enc',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    sc_t = device('nicos.devices.generic.MultiSwitcher',
        description = 'Sample Changer 2 Huber device',
        moveables = ['sc_t_y', 'st1_z'],
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
        lowlevel = False,
    ),
)

alias_config = {
    'SampleChanger': {'sc_t': 100},
}
