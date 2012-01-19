
includes = ['system']

devices = dict(
    chdelaybus = device('nicos.toftof.toni.ModBus',
                   tacodevice = 'toftof/rs232/ifchdelay',
                   lowlevel = True),
    chdelay   = device('nicos.toftof.toni.DelayBox',
                   bus = 'chdelaybus',
                   addr = 0xF1,
                   unit = '', # ???
                   fmtstr = '%d'),
)
