from __future__ import absolute_import, division, print_function

from nicos_ess.nexus import DeviceAttribute, DeviceDataset, NXDataset, NXLink
from nicos_sinq.amor.nexus.placeholder import UserEmailPlaceholder

# Default template for AMOR including most of the devices
amor_default = {
    "NeXus_Version": "4.3.0",
    "instrument": "AMOR",
    "owner": DeviceAttribute('Amor', 'responsible'),
    "entry1:NXentry": {
        "comment": DeviceDataset('Exp', 'remark'),
        "title": DeviceDataset('Exp', 'title'),
        "amor_mode": DeviceDataset('Exp', 'mode'),
        "proposal_id": DeviceDataset('Exp', 'proposal'),
        "start_time": DeviceDataset('dataset', 'starttime'),
        "user:NXuser": {
            "email": NXDataset(UserEmailPlaceholder('Exp', 'users', True)),
            "name": NXDataset(UserEmailPlaceholder('Exp', 'users', False)),
        },
        "area_detector": NXLink('AMOR/area_detector'),
        "single_detector_1": NXLink('AMOR/single_detector_1'),
        "single_detector_2": NXLink('AMOR/single_detector_2'),
        "AMOR:NXinstrument": {
            "name": DeviceDataset('Amor', 'instrument'),
            "definition": NXDataset(
                'TOFNREF', dtype='string',
                url="http://www.neutron.anl.gov/nexus/xml/NXtofnref.xml"),
            "SINQ:NXSource": {
                "name": NXDataset('SINQ'),
                "type": NXDataset('Continuous flux spallation source')
            }
        },
        "sample:NXsample": {}
    }
}

# Template that saves only the detector data
detector_only = {
    "entry1:NXentry": {
        "area_detector": NXLink('AMOR/area_detector'),
        "AMOR:NXinstrument": {
            "name": DeviceAttribute("Amor", "instrument")
        },
    }
}

# Template that saves only the sample data
sample_only = {
    "entry1:NXentry": {
        "sample:NXsample": {}
    }
}

from .instrument_components import detectors, instrument, \
    instrument_removable, sample

amor_default["entry1:NXentry"]["AMOR:NXinstrument"].update(detectors)
amor_default["entry1:NXentry"]["AMOR:NXinstrument"].update(instrument)
amor_default["entry1:NXentry"]["AMOR:NXinstrument"].update(instrument_removable)

detector_only["entry1:NXentry"]["AMOR:NXinstrument"].update(detectors)

amor_default["entry1:NXentry"]["sample:NXsample"].update(sample)

sample_only["entry1:NXentry"]["sample:NXsample"].update(sample)
