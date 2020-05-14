from nicos_ess.nexus import DeviceAttribute, DeviceDataset, \
    NXDataset, EventStream, NXLink
from nicos_ess.nexus.elements import CacheStream
from nicos_sinq.nexus.fwplaceholder import DevArrayPlaceholder

# Default template for DMC including most of the devices
dmc_default = {
    "NeXus_Version": "4.4.0",
    "instrument": "DMC",
    "owner": DeviceAttribute('DMC', 'responsible'),
    "entry:NXentry": {
        "title": DeviceDataset('Exp', 'title'),
        "user:NXuser": {
            "name": DeviceDataset('Exp', 'users'),
            "email": DeviceDataset('Exp', 'localcontact')
        },
        "proposal_id": DeviceDataset('Exp', 'proposal'),
        "start_time": DeviceDataset('dataset', 'starttime'),
        "sample:NXsample": {
            "name": DeviceDataset('Sample', 'samplename'),
            "rotation_angle": DeviceDataset('som'),
            "temperature": NXDataset([0], dtype='float', units='K'),
            "temperature_mean": NXDataset([0], dtype='float', units='K'),
            "temperature_stddev": NXDataset([0], dtype='float', units='K'),
            "polar_angle": DeviceDataset('m2t'),
        },
        "monitor:NXmonitor": {
            'data': CacheStream('c1', 'int'),
            'time': CacheStream('elapsedtime', dtype='float'),
            'count_mode': DeviceDataset('dmcdet', 'mode', 'string'),
            'preset': DeviceDataset('dmcdet', 'preset'),
        },
        "DMC:NXinstrument": {
            "SINQ:NXSource": {
                "name": NXDataset('SINQ'),
                "type": NXDataset('Continuous flux spallation source')
            },
            "monochromator:NXmonochromator": {
                "chi": DeviceDataset('mtchi'),
                "curvature": DeviceDataset('mtcurve'),
                "d_spacing": DeviceDataset('wavelength','dvalue'),
                "wavelength": DeviceDataset('wavelength'),
                "phi": DeviceDataset('mtphi'),
                "rotation_angle": DeviceDataset('mth'),
                "type": NXDataset('Pyrolithic Graphite',type='string'),

                "x_translation": DeviceDataset('mtx'),
                "y_translation": DeviceDataset('mty')
            },
            "detector:NXdetector": {
                "s2t": DeviceDataset('s2t'),
                "polar_angle": NXDataset(DevArrayPlaceholder('s2t', .2, 200)),
                "data:NXevent_data": {
                    "data": EventStream('DMC_data','DMC@SINQ',
                                        'localhost:9092', dtype='uint32'),
                },
            }
        },
        "data:NXdata": {
            "data": NXLink('/entry/DMC/detector/data')
        }
    }
}
