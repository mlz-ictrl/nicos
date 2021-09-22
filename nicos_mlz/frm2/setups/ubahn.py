description = 'next subway departure'

group = 'lowlevel'

devices = dict(
    UBahn = device('nicos_mlz.devices.mvg.MVG',
        description = 'Next departure of the U-Bahn from station '
                      'Garching-Forschungszentrum to the Munich center',
        tangodevice='tango://ictrlfs.ictrl.frm2.tum.de:10000/mvg/U6/departures',
        limit =3 ,
    ),
)
