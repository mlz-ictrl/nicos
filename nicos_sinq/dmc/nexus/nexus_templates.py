from nicos_ess.nexus import DeviceAttribute, DeviceDataset, NXDataset

# Default template for DMC including most of the devices
dmc_default = {
    "NeXus_Version": "4.3.0",
    "instrument": "DMC",
    "owner": DeviceAttribute('DMC', 'responsible'),
    "entry1:NXentry": {
        "title": DeviceDataset('Exp', 'title'),
        "user:NXuser": {
            "name": DeviceDataset('Exp', 'users'),
            "email": DeviceDataset('Exp', 'localcontact')
        },
        "sample:NXsample": {
            "sample_name": DeviceDataset('Sample', 'samplename'),
            "sample_table_rotation": DeviceDataset('som'),
            "sample_temperature": NXDataset([0], dtype='float', units='K'),
            "temperature_mean": NXDataset([0], dtype='float', units='K'),
            "temperature_stddev": NXDataset([0], dtype='float', units='K')
        },
        "DMC:NXinstrument": {
            "chi" : DeviceDataset('mtchi'),
            "curvature" : DeviceDataset('mtcurve'),
            "d_spacing" : DeviceDataset('wavelength','dvalue'),
            "lambda" : DeviceDataset('wavelength'),
            "phi" : DeviceDataset('mtphi'),
            "theta" :DeviceDataset('mth'),
            "two_theta" :DeviceDataset('m2t'),
            # "type" :,
            "x_translation" :DeviceDataset('mtx'),
            "y_translation" :DeviceDataset('mty')
        }
    }
}
