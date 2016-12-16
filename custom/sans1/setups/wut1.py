description = 'wut readout'

includes = []

# group = 'lowlevel'

devices = dict(
    s1_wut1 = device('sans1.wut.WutValue',
                            #hostname = 'sans1wut1.office.frm2',
                            hostname = '172.25.49.24',
                            port = '1',
                            description = 'sensor 1 of wut box 1',
                            fmtstr = '%.2F',
                            lowlevel = False,
                            loglevel = 'info',
                            unit = 'V',
    ),
    s2_wut2 = device('sans1.wut.WutValue',
                            hostname = '172.25.49.24',
                            port = '2',
                            description = 'sensor 2 of wut box 1',
                            fmtstr = '%.2F',
                            lowlevel = False,
                            loglevel = 'info',
                            unit = 'V',
    ),
)
