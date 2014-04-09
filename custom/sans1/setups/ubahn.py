description = 'next subway departure'
group = 'lowlevel'

devices = dict(
    UBahn = device('frm2.ubahn.UBahn',
                   description = 'departure of next subway',
                   fmtstr='%s',
                  ),
)
