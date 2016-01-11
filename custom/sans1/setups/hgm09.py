description = 'Gaussmeter for Sans1 Magnet'

group = 'optional'

nethost = 'testbox.se.frm2'

devices = dict(
    hgm09 = device('antares.hgm09.HGM09',
                   description = 'Gaussmeter for ccmsans',
                   tacodevice = '//%s/test/rs232/ttyacm0' % (nethost, ),
                   fmtstr = '%.3f',
                   maxage = 120,
                   pollinterval = 15,
                   tacotimeout = 5,
                  ),
)
startupcode = """
"""
