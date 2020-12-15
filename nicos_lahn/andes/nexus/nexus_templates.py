from nicos_sinq.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceDataset, ImageDataset, NXLink, NXTime
from nicos_sinq.nexus.nexussink import NexusTemplateProvider

andes_default = {
     "NeXus_Version": "nexusformat v0.5.3",
     "instrument": "ANDES",
     "owner": DeviceDataset('Andes', 'responsible'),
     "entry:NXentry": {
              "title": DeviceDataset('Exp', 'title'),
              "proposal_id": DeviceDataset('Exp', 'proposal'),
              "start_time": NXTime(),
              "end_time": NXTime(),
              "user:NXuser": {
                      "name": DeviceDataset('Exp', 'users'),
                      "email": DeviceDataset('Exp', 'localcontact'),
               },
              "ANDES:NXinstrument": {
                       "source:NXsource": {
                                 "type": ConstDataset('Reactor Neutron Source', 'string'),
                                 "name": ConstDataset('RA10', 'string'),
                                 "probe": ConstDataset('neutron', 'string'),
                       },
                       "detector:NXdetector": {
                                   "polar_angle": DeviceDataset('stt'),
                                   "data": ImageDataset(0, 0),
                                   "distance": DeviceDataset('lsd'),
                       },
                       "monochromator:NXmonochromator": {
                                        "polar_angle": DeviceDataset('mtt'),
                                        "crystal:NXcrystal": {
                                                   "type": DeviceDataset('crystal'),
                                        },
                                        "d_spacing": DeviceDataset('wavelength', 'dvalue'),
                                        "wavelength": DeviceDataset('wavelength', dtype='float', units='angstrom'),
                       }
              },
              "sample:NXsample": {
                        "name": DeviceDataset('Sample', 'samplename'),
                        "distance": DeviceDataset('lms'),
                        "x_translation": DeviceDataset('x'),
                        "y_translation": DeviceDataset('y'),
                        "z_translation": DeviceDataset('z'),
                        "rotation_angle": DeviceDataset('phi'),
              },
              "monitor:NXmonitor": {
                         "mode": ConstDataset('timer', 'string'),
                         "preset": DetectorDataset('timer', 'float32'),
                         "integral": DetectorDataset('monitor', 'int32'),
              },
              "data:NXdata": {
                      "data": NXLink('/entry/ANDES/detector/data')
              },
        }
}


class ANDESTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        return andes_default
