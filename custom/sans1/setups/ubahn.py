description = 'next subway departure'
group = 'lowlevel'

devices = dict(
    UBahn = device('frm2.ubahn.UBahn', fmtstr='%s'),
    OutsideTemp = device('mira.meteo.Temp'),
)
