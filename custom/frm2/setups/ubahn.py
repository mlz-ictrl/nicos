description = 'next subway departure'
group = 'lowlevel'

devices = dict(
    UBahn = device('nicos_mlz.frm2.devices.ubahn.UBahn',
                   description = 'Next departure of the U-Bahn from station '
                                 'Garching-Forschungszentrum to the Munich '
                                 'center',
                   fmtstr='%s',
                  ),
)
