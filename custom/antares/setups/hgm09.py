description = 'HGM09 Hand Gauss Meter'
group = 'optional'

includes = []

devices = dict(
    hgm09 = device('antares.hgm09.HGM09',
                   description = 'HGM09 Hand Gauss Meter',
                   tacodevice = 'antares/rs232/hgm09',
                  ),
)

startupcode = '''
'''
