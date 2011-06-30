name = 'cascade psd detector'

devices = dict(
    psd   = device('nicos.mira.cascade.CascadeDetector',
                   server = 'cascade.mira.frm2:1234'),

    PSDHV = device('nicos.mira.iseg.IsegHV',
                   tacodevice = 'mira/network/detectorrs_4',
                   abslimits = (-3000, 0),
                   pollinterval = 10,
                   maxage = 20,
                   channel = 1),

)

