description = 'virtual LAUE devices'
group = 'basic'

sysconfig = dict(
)

tangohost = '%s:10000' % 'lauecounter.laue.frm2'

devices = dict(
    FileSaver = device('laue.fileformats.ASCIIFileFormat',
                       description = 'Saves TOF data in ASCII format',
                      ),
    det = device('devices.tango.TofDetector',
                 description = 'TOF detector device',
                 tangodevice = 'tango://%s/laue/tof/detector' % tangohost,
                 timer = 'tango://%s/laue/tof/timer' % tangohost,
                 subdir = '.',
                 fileformats = ['FileSaver', ],
                ),
)

startupcode = '''
SetDetectors(det)
SetEnvironment()
printinfo("============================================================")
printinfo("Welcome to the NICOS LAUE test setup.")
printinfo("============================================================")
'''
