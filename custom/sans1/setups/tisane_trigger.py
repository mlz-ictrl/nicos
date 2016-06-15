description = 'tisane_trigger'

includes = []

#group = 'lowlevel'

devices = dict(
    tisane_trigger = device('sans1.tisane_trigger.WutValue',
                            hostname = 'sans1tisane-trigger.sans1.frm2',
                            port = '1',
                            description = 'sensor 1 of wut box 1',
                            fmtstr = '%.2F',
                            lowlevel = False,
                            loglevel = 'info',
                            unit = 'V',
    ),
)

