from nicos_ess.nexus import DeviceAttribute, DeviceDataset, NXDataset, NXLink
from nicos_sinq.nexus.elements import NXTime
from nicos_sinq.nexus.nexussink import NexusTemplateProvider

andes_default = {
     "NeXus_Version": "nexusformat v0.5.3",
     "instrument": "ANDES",
     "owner": DeviceAttribute('LAHN', 'responsible'),
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
                                 "type": NXDataset('Reactor Neutron Source'),
                                 "name": NXDataset('RA10'),
                                 "probe": NXDataset('neutron'),
                       },
                       "detector:NXdetector": {
                                   "polar_angle": DeviceDataset('stt'),
                                   "data": DeviceDataset('cam', 'images'),
                                   "distance": DeviceDataset('lsd'),
                       },
                       "monochromator:NXmonochromator": {
                                        "polar_angle": DeviceDataset('mtt'),
                                        "crystal:NXcrystal": {
                                                   "type": DeviceDataset('crystal'),
                                        },
                                        "d_spacing": DeviceDataset('wavelength','dvalue'),
                                        "wavelength": NXDataset('wavelength', dtype='float', units='angstrom'),
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
                         "mode": NXDataset('timer'),
                         "preset": DeviceDataset('cam', 'timers'),
                         "integral": DeviceDataset('cam', 'monitors'),
              },
              "data:NXdata": {
                      "data": NXLink('/entry/ANDES/detector/data')
              },
        }
}

class ANDESTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        return andes_default
