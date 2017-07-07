description = 'radiation monitor over MIRA'
group = 'lowlevel'

devices = dict(
    DoseRate = device('nicos_mlz.mira.radmon.RadMon',
                      description = 'dose rate measured by guide hall monitor',
                      fmtstr = '%.3g',
                      unit = 'uSv/h',
                     ),
)
