description = 'Bruker OPUS FTIR spectrometer'
group = 'optional'

tango_base = 'tango://localhost:10000/dls02/'

devices = dict(
    opus = device('nicos_jcns.dls02.devices.bruker_opus.OpusChannel',
        description = 'Bruker OPUS FTIR spectrometer',
        tangodevice = tango_base + 'opus/channel',
    ),
)

startupcode = '''
AddDetector(opus)
'''
