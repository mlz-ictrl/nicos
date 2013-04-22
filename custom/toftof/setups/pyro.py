description = 'Impac IGAR 12-LO pyrometer'

group = 'optional'

includes = ['system', 'alias_T']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    pyro = device('toftof.impac.ImpacPyrometer',
                  tacodevice = '//%s/toftof/rs232/ifpyrometer' % (nethost, ),
                  unit = 'C',
                  fmtstr = '%.3f',
                 ),
)

startupcode = """
"""
