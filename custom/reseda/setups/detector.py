description = 'standard detector and counter card'
group = 'lowlevel'

includes = []

devices = dict(
    timer = device('devices.taco.FRMTimerChannel',
        tacodevice = '//resedasrv/reseda/frmctr/dev0',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    mon1 = device('devices.taco.FRMCounterChannel',
        tacodevice = '//resedasrv/reseda/frmctr/dev1',
        type = 'monitor',
        fmtstr = '%d',
        lowlevel = True,
    ),
    mon2 = device('devices.taco.FRMCounterChannel',
        tacodevice = '//resedasrv/reseda/frmctr/dev2',
        type = 'monitor',
        fmtstr = '%d',
        lowlevel = True,
    ),
    ctr1 = device('devices.taco.FRMCounterChannel',
        tacodevice = '//resedasrv/reseda/frmctr/dev3',
        type = 'counter',
        fmtstr = '%d',
        lowlevel = True,
    ),
)
