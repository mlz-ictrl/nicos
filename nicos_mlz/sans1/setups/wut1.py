description = 'wut readout'

includes = []

# group = 'lowlevel'

devices = dict(
    s1_wut1 = device('nicos_mlz.sans1.devices.wut.WutValue',
                     hostname = 'sans1wut1.sans1.frm2',
                     port = '1',
                     description = 'sensor 1 of wut box 1',
                     fmtstr = '%.2F',
                     lowlevel = False,
                     loglevel = 'info',
                     unit = 'V',
    ),
    s2_wut2 = device('nicos_mlz.sans1.devices.wut.WutValue',
                     hostname = 'sans1wut1.sans1.frm2',
                     port = '2',
                     description = 'sensor 2 of wut box 1',
                     fmtstr = '%.2F',
                     lowlevel = False,
                     loglevel = 'info',
                     unit = 'V',
    ),
)
