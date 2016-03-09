description = 'virtual LAUE devices'
group = 'basic'

sysconfig = dict(
)

tango_base = 'tango://lauecounter.laue.frm2:10000/laue/'

devices = dict(
    FileSaver = device('laue.fileformats.ASCIIFileFormat',
                       description = 'Saves TOF data in ASCII format',
                      ),
    # TODO: fix this (use TOFChannel and generic.Detector)
    # det = device('devices.tango.TofDetector',
    #              description = 'TOF detector device',
    #              tangodevice = tango_base + 'tof/detector',
    #              timer = tango_base + 'tof/timer',
    #              subdir = '.',
    #              fileformats = ['FileSaver', ],
    #             ),
)

startupcode = '''
SetDetectors(det)
SetEnvironment()
printinfo("============================================================")
printinfo("Welcome to the NICOS LAUE test setup.")
printinfo("============================================================")
'''
