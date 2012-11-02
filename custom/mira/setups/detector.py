description = 'standard detector and counter card'
group = 'lowlevel'

includes = ['base']

devices = dict(
    timer    = device('devices.taco.FRMTimerChannel',
                      tacodevice = '//mirasrv/mira/frmctr/at',
                      fmtstr = '%.2f',
                      lowlevel = True),
    mon1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = '//mirasrv/mira/frmctr/a1',
                      type = 'monitor',
                      fmtstr = '%d',
                      lowlevel = True),
    mon2     = device('devices.taco.FRMCounterChannel',
                      tacodevice = '//mirasrv/mira/frmctr/a2',
                      type = 'monitor',
                      fmtstr = '%d',
                      lowlevel = True),
    ctr1     = device('devices.taco.FRMCounterChannel',
                      tacodevice = '//mirasrv/mira/frmctr/a3',
                      type = 'counter',
                      fmtstr = '%d',
                      lowlevel = True),

    det      = device('devices.taco.FRMDetector',
                      timer  = 'timer',
                      monitors = ['mon1', 'mon2'],
                      counters = ['ctr1'],
                      fmtstr = 'timer %s, mon1 %s, mon2 %s, ctr1 %s',
                      maxage = 2,
                      pollinterval = 0.5),

    DetHV     = device('mira.iseg.IsegHV',
                       tacodevice = 'mira/network/rs12_2',
                       channel = 1,
                       pollinterval = 10,
                       maxage = 20,
                       abslimits = (0, 950),
                       fmtstr = '%d',
                       ),

    MonHV     = device('mira.iseg.IsegHV',
                       tacodevice = 'mira/network/rs7_4',
                       channel = 1,
                       abslimits = (0, 500),
                       pollinterval = 10,
                       maxage = 30,
                       fmtstr = '%d',
                       ),
)
