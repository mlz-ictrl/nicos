description = 'pressure filter readout'

includes = []

group = 'lowlevel'

devices = dict(
    p_in_filter = device('nicos_mlz.sans1.devices.wut.WutValue',
                         hostname = 'sans1wut-p-diff-fak40.sans1.frm2',
                         port = '1',
                         description = 'pressure in front of filter',
                         fmtstr = '%.2F',
                         lowlevel = False,
                         loglevel = 'info',
                         unit = 'bar',
    ),
    p_out_filter = device('nicos_mlz.sans1.devices.wut.WutValue',
                          hostname = 'sans1wut-p-diff-fak40.sans1.frm2',
                          port = '2',
                          description = 'pressure behind of filter',
                          fmtstr = '%.2F',
                          lowlevel = False,
                          loglevel = 'info',
                          unit = 'bar',
    ),
    p_diff_filter = device('nicos_mlz.sans1.devices.wut.WutDiff',
                           hostname = 'sans1wut-p-diff-fak40.sans1.frm2',
                           description = 'pressure in front of filter minus pressure behind filter',
                           fmtstr = '%.2F',
                           lowlevel = False,
                           loglevel = 'info',
                           unit = 'bar',
    ),
)
