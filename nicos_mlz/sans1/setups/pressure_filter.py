description = 'pressure filter readout'

group = 'lowlevel'

devices = dict(
    p_in_filter = device('nicos_mlz.sans1.devices.wut.WutReadValue',
        hostname = 'sans1wut-p-diff-fak40.sans1.frm2',
        port = 1,
        description = 'pressure in front of filter',
        fmtstr = '%.2F',
        lowlevel = False,
        loglevel = 'info',
        unit = 'bar',
    ),
    p_out_filter = device('nicos_mlz.sans1.devices.wut.WutReadValue',
        hostname = 'sans1wut-p-diff-fak40.sans1.frm2',
        port = 2,
        description = 'pressure behind filter',
        fmtstr = '%.2F',
        lowlevel = False,
        loglevel = 'info',
        unit = 'bar',
    ),
    p_diff_filter = device('nicos.devices.generic.CalculatedReadable',
        description = 'pressure in front of filter minus pressure behind filter',
        device1 = 'p_in_filter',
        device2 = 'p_out_filter',
        op = '-',
        fmtstr = '%.2F',
        lowlevel = False,
        loglevel = 'info',
    ),
)
