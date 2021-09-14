description = 'MVG departures from Garching-Forschungszentrum'

devices = dict(
    U6 = device('nicos_mlz.devices.mvg.MVG',
        description = 'Next subway departures',
        tangodevice='tango://ictrlfs.ictrl.frm2.tum.de:10000/mvg/U6/departures',
        limit =3 ,
        displaymode='time'
    ),
    Bus230 = device('nicos_mlz.devices.mvg.MVG',
        description = 'Next bus 230(Haar) departures',
        tangodevice='tango://ictrlfs.ictrl.frm2.tum.de:10000/mvg/Bus230/departures',
        deltaoffset=15*60,
    ),
    Bus292 = device('nicos_mlz.devices.mvg.MVG',
        description = 'Next bus 292(Oberschlessheim) departures',
        tangodevice='tango://ictrlfs.ictrl.frm2.tum.de:10000/mvg/Bus292/departures',
    ),
    Bus690 = device('nicos_mlz.devices.mvg.MVG',
        description = 'Next bus 690(Eching) departures',
        tangodevice='tango://ictrlfs.ictrl.frm2.tum.de:10000/mvg/Bus690/departures',
    ),
    )
display_order = 99
