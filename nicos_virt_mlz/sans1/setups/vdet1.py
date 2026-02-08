description = 'qmesydaq devices for SANS1'

# included by vsans1
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['BerSANSFileSaver',
                 # 'LivePNGSink', 'LivePNGSinkLog',
                 # 'DetectorSetup', 'DetectorCalibration'
                 ],
)

excludes = ['det1']

devices = dict(
    BerSANSFileSaver = device('nicos_mlz.sans1.datasinks.BerSANSImageSink',
        description = 'Saves image data in BerSANS format',
        filenametemplate = [
            'D%(pointcounter)07d.001',
        ],
        subdir = 'hist',
    ),
    mcstas = device('nicos_virt_mlz.sans1.devices.detector.McStasSimulation',
        description = 'McStas simulation',
        pollinterval = None,
        wl = 'wl',
        dlambda = 'selector_delta_lambda',
        nose_slit = 'sa2',
        sd = 'det1_z',
        tilt = 'selector_tilt',
        det1rot = 'det1_omg',
        det1x = 'det1_x',
        samplepos = 'st_x',
        coll = 'col',
        sword = 'ccmsanssc_position',
        neutronspersec = {
            'localhost': 1.e7,
            'taco6.ictrl.frm2.tum.de': 8.9e+05,
            # configdata('config_data.host'): 1.12e5,
        },
    ),
    det1_mon1 = device('nicos.devices.generic.VirtualCounter',
        description = 'QMesyDAQ Counter0',
        type = 'monitor',
    ),
    det1_mon2 = device('nicos.devices.generic.VirtualCounter',
        description = 'QMesyDAQ Counter1',
        type = 'monitor',
    ),
    det1_mon3 = device('nicos.devices.generic.VirtualCounter',
        description = 'QMesyDAQ Counter2 (reference for tisane)',
        type = 'monitor',
    ),
    det1_ev = device('nicos.devices.generic.VirtualCounter',
        description = 'QMesyDAQ Events channel',
        type = 'counter',
    ),
    det1_timer = device('nicos.devices.generic.VirtualTimer',
        description = 'QMesyDAQ Timer',
    ),
    det1_image = device('nicos_virt_mlz.toftof.devices.detector.Image',
        description = 'Image data device',
        mcstas = 'mcstas',
        mcstasfile = 'detector_output.dat',
        size = (1024, 1024),
        fmtstr = '%d',
        unit = 'cts',
        pollinterval = 86400,
        visibility = (),
    ),
)
