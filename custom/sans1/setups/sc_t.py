description = 'sample changer temperature device'

group = 'optional'

includes = ['sample_changer', 'sample_table_1']

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    sc_t_y       = device('devices.generic.Axis',
                         description = 'Sample Changer 1/2/t Axis',
                         pollinterval = 15,
                         maxage = 60,
                         fmtstr = '%.2f',
                         abslimits = (-0, 600),
                         precision = 0.01,
                         motor = 'sc_t_ymot',
                         coder = 'sc_t_yenc',
                         obs=[],
                        ),
    sc_t_ymot    = device('devices.taco.motor.Motor',
                         description = 'Sample Changer 1/2/t Axis motor',
                         tacodevice = '//%s/sans1/samplechanger/y-sc1mot' % (nethost, ),
                         fmtstr = '%.2f',
                         abslimits = (-0, 600),
                         lowlevel = True,
                        ),
    sc_t_yenc    = device('devices.taco.coder.Coder',
                         description = 'Sample Changer 1/2/t Axis encoder',
                         tacodevice = '//%s/sans1/samplechanger/y-sc1enc' % (nethost, ),
                         fmtstr = '%.2f',
                         lowlevel = True,
                        ),

    sc_t    = device('devices.generic.MultiSwitcher',
                    description = 'Sample Changer 2 Huber device',
                    moveables = ['sc_t_y', 'st1_z'],
                    mapping = {11:  [592.50, -4.6], 10: [535.00, -4.0],
                                9:  [476.50, -4.0],  8: [418.00, -4.0],
                                7:  [358.75, -4.0],  6: [300.50, -4.0],
                                5:  [241.50, -4.0],  4: [182.00, -4.0],
                                3:  [123.00, -4.0],  2: [ 65.50, -4.0],
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
