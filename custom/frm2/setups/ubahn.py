description = 'next subway departure'
group = 'lowlevel'

devices = dict(
    UBahn = device('frm2.ubahn.UBahn',
                   description = 'Next departure of the U-Bahn from station '
                                 'Garching-Forschungszentrum to the Munich '
                                 'center',
                   fmtstr='%s',
                  ),
)
