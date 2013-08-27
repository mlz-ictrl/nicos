description = 'radiation monitor over MIRA'
devices = dict(
    DoseRate = device('mira.radmon.RadMon', fmtstr='%.3g', unit='uSv/h'),
)
