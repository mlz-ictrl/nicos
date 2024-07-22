from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, ImageDataset, NXAttribute, NXLink, \
    NXScanLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_sinq.nexus.specialelements import DevStat, SaveSampleEnv, \
    TwoThetaArray

# Default template for HRPT including most of the devices
hrpt_default = {"NeXus_Version": "4.3.0", "instrument": "HRPT",
                "owner": DeviceAttribute('Exp', 'users'),
                "entry1:NXentry": {"title": DeviceDataset('Exp', 'title'),
                                   "proposal_title":
                                       DeviceDataset('Exp', 'proposal_title'),
                                   "proposal_id": DeviceDataset('Exp',
                                                                'proposal'),
                                   "start_time": NXTime(),
                                   "definition": ConstDataset('NXmonopd',
                                                              'string'),
                                   "end_time": NXTime(),
                                   "user:NXuser": {
                                       "name": DeviceDataset('Exp', 'users'),
                                       "email": DeviceDataset('Exp',
                                                              'user_email')},
                                   "proposal_user:NXuser": {
                                       "name": DeviceDataset('Exp', 'users'),
                                   },
                                   "sample:NXsample": {
                                       "sample_name":
                                           DeviceDataset('Sample',
                                                         'samplename'),
                                       "name": NXLink(
                                           '/entry1/sample/sample_name'),
                                       "sample_table_rotation": DeviceDataset(
                                           'som'),
                                       "rotation_angle": NXLink(
                                           '/entry1/sample/'
                                           'sample_table_rotation'),
                                       "x_translation":
                                           DeviceDataset('stx',
                                                         dtype='float32'),
                                       "y_translation":
                                           DeviceDataset('sty',
                                                         dtype='float32'),
                                       "sample_changer_position":
                                           DeviceDataset('chpos',
                                                         dtype='float32'),
                                       "sample_rotation_state": DeviceDataset(
                                           'som_oscillation'),
                                       "sample_mur": DeviceDataset('Sample',
                                                                   'mur'),
                                       "hugo": SaveSampleEnv(),
                                       "temperature_mean":
                                           DevStat("Ts:avg"),
                                       "temperature_stddev":
                                           DevStat("Ts:stddev"),
                                   }, "HRPT:NXinstrument": {
                        "HRPT-CERCA-Detector:NXpsd": {
                            "CounterMode": DetectorDataset('mode', "string"),
                            "Monitor": DetectorDataset('monitor1', 'float32',
                                                       units=NXAttribute(
                                                           'counts',
                                                           'string')),
                            "Preset": DetectorDataset('preset', 'float32'),
                            "Step": ConstDataset(.01, 'float32'),
                            "beam_monitor": DetectorDataset('monitor2',
                                                            'int32',
                                                            units=NXAttribute(
                                                                'counts',
                                                                'string')),
                            "number_of_steps": ConstDataset(1600, 'int32'),
                            "proton_monitor":
                                DetectorDataset('protoncount',
                                                dtype='int32',
                                                units=NXAttribute(
                                                                  'counts',
                                                                  'string')),
                            "radial_collimator_status":
                                DeviceDataset('racoll'),
                            "radial_collimator_type":
                                DeviceDataset('racoll', parameter='type'),
                            "time":
                                DetectorDataset('elapsedtime', 'float32'),
                            "two_theta_start": DeviceDataset('s2t',
                                                             dtype='float32'),
                            "two_theta":
                                TwoThetaArray('s2t', .1, 1600,
                                              axis=NXAttribute(1, 'int32')),
                            "counts":
                                ImageDataset(0, 0,
                                             signal=NXAttribute(1, 'int32')),
                            "polar_angle": NXLink(
                                '/entry1/HRPT/HRPT-CERCA-Detector/two_theta'),
                            "data": NXLink(
                                '/entry1/HRPT/HRPT-CERCA-Detector/counts'), },
                        "Kollimator1:NXcollimator": {
                            "kollimator1": DeviceDataset('cex1',
                                                         units=NXAttribute(
                                                                    'degrees',
                                                                    'string')),
                            "kollimator2": DeviceDataset('cex2',
                                                         units=NXAttribute(
                                                             'degrees',
                                                             'string')), },
                        "Monochromator:NXmonochromator": {
                            "curvature_lower": DeviceDataset('mcvl'),
                            "omega_lower": DeviceDataset('moml',
                                                         units=NXAttribute(
                                                             'degree',
                                                             'string')),
                            "paralell_tilt_lower":
                                DeviceDataset('mgpl'),
                            "paralell_translation_lower":
                                DeviceDataset('mtpl'),
                            "vertical_tilt_lower": DeviceDataset('mgvl'),
                            "vertical_translation_lower":
                                DeviceDataset('mtvl'),
                            "curvature_upper": DeviceDataset('mcvu'),
                            "omega_upper": DeviceDataset('momu'),
                            "paralell_tilt_upper": DeviceDataset('mgpu'),
                            "paralell_translation_upper":
                                DeviceDataset('mtpu'),
                            "vertical_tilt_upper": DeviceDataset('mgvu'),
                            "vertical_translation_upper":
                                DeviceDataset('mtvu'),
                            "lift": DeviceDataset('mexz',
                                                  units=NXAttribute('mm',
                                                                    'string')),
                            "lambda": DeviceDataset('wavelength',
                                                    dtype='float32',
                                                    units=NXAttribute(
                                                        'Angstroem',
                                                        'string')),
                            "type": ConstDataset('GE', 'string'), },
                        "crystal:NXcrystal": {
                            'wavelength': NXLink(
                                '/entry1/HRPT/Monochromator/lambda'), },
                        "SINQ:NXsource": {
                            "name": ConstDataset('SINQ', 'string'),
                            "type": ConstDataset('Spallation Neutron Source',
                                                 'string'),
                            "probe": ConstDataset('neutron', 'string'), },
                        "beam_reduction:NXslit": {
                            "left": DeviceDataset('brle', dtype='float32'),
                            "right": DeviceDataset('brri', dtype='float32'),
                            "top": DeviceDataset('brto', dtype='float32',),
                            "bottom": DeviceDataset('brbo', dtype='float32')},
                        "exit_slit:NXslit": {
                            "left": DeviceDataset('d1l', dtype='float32'),
                            "right": DeviceDataset('d1r', dtype='float32'),
                            "width": DeviceDataset('slit1_width'),
                        }
                    },
                    'monitor:NXmonitor':
                                       {
                                       'mode':
                                           NXLink(
                                             '/entry1/HRPT/HRPT-CERCA'
                                             '-Detector/CounterMode'),
                                       'preset': NXLink(
                                           '/entry1/HRPT/HRPT-CERCA-Detector'
                                           '/Preset'),
                                       'integral': NXLink(
                                           '/entry1/HRPT/HRPT-CERCA-Detector/'
                                           'Monitor'), },
                    "data1:NXdata": {
                                       'counts': NXLink(
                                           '/entry1/HRPT/HRPT-CERCA-Detector'
                                           '/counts'),
                                       'Step': NXLink(
                                           '/entry1/HRPT/'
                                           'HRPT-CERCA-Detector/Step'),
                                       'Monitor': NXLink(
                                           '/entry1/HRPT/HRPT-CERCA-Detector'
                                           '/Monitor'),
                                       'no_of_steps': NXLink(
                                           '/entry1/HRPT/HRPT-CERCA-Detector/'
                                           'number_of_steps'),
                                       'lambda': NXLink(
                                           '/entry1/HRPT/'
                                           'Monochromator/lambda'),
                                       'None': NXScanLink(),
                                       'data': NXLink(
                                           '/entry1/HRPT/HRPT-CERCA-Detector/'
                                           'counts'),
                                       'polar_angle': NXLink(
                                           '/entry1/HRPT/HRPT-CERCA-Detector/'
                                           'two_theta'), }, }}


class HRPTTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        return hrpt_default
