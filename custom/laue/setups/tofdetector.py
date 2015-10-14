description = 'virtual LAUE devices'
group = 'basic'

sysconfig = dict(
)

tangohost = '%s:10000' % 'taco61.ictrl.frm2'

devices = dict(
    FileSaver = device('nicos.laue.fileformats.ASCIIFileFormat',
                       description = 'Saves TOF data in ASCII format',
                      ),
    det = device('nicos.devices.tango.TofDetector',
                 description = 'TOF detector device',
                 tangodevice = 'tango://%s/test/tof/detector' % tangohost,
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
