description = 'THM1176 gaussmeter probe for magnetic field measurements'
group = 'optional'

devices = dict(
    Bf = device('nicos.devices.vendor.metrolab.THM1176',
        description = 'THM 1176 gaussmeter',
        device = '/dev/usbtmc_THM1176',
        usbdevice = '/dev/usb_THM1176',
    ),
)

startupcode = '''
AddDetector(Bf)
'''
