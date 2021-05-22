from nicos_ess.nexus import DeviceAttribute, DeviceDataset, EventStream, \
    NXDataset, NXLink
from nicos_sinq.amor.nexus.placeholder import DistancesPlaceholder, \
    UserEmailPlaceholder

from .instrument_components import detectors, instrument, \
    instrument_removable, sample

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


amor_default["entry1:NXentry"]["AMOR:NXinstrument"].update(detectors)
amor_default["entry1:NXentry"]["AMOR:NXinstrument"].update(instrument)
amor_default["entry1:NXentry"]["AMOR:NXinstrument"].update(
    instrument_removable)

detector_only["entry1:NXentry"]["AMOR:NXinstrument"].update(detectors)

amor_default["entry1:NXentry"]["sample:NXsample"].update(sample)

sample_only["entry1:NXentry"]["sample:NXsample"].update(sample)


amor_commissioning = {
    'instrument:NXentry': {
        'name': 'amor',
        'facility': NXDataset('SINQ'),
        'stages:NXcollection': {
            'som:NXevent_data': {
                'position': EventStream(
                    topic='AMOR_metadata',
                    source='SQ:AMOR:motc:som.RBV',
                    mod='f142',
                    dtype='double',
                ),
                'unit': 'deg',
            },
            'soz:NXevent_data': {
                'position': EventStream(
                    topic='AMOR_metadata',
                    source='SQ:AMOR:motc:soz.RBV',
                    mod='f142',
                    dtype='double',
                ),
                'units': 'mm',
            },
            'com:NXevent_data': {
                'position': EventStream(
                    topic='AMOR_metadata',
                    source='SQ:AMOR:motc:com.RBV',
                    mod='f142',
                    dtype='double',
                ),
                'units': 'deg',
            },
            'coz:NXevent_data': {
                'position': EventStream(
                    topic='AMOR_metadata',
                    source='SQ:AMOR:motc:coz.RBV',
                    mod='f142',
                    dtype='double',
                ),
                'units': 'mm',
            },
        },
        'diaphragms:NXcollection': {
            'virtual source:NXcollection': {
                'vertical:NXevent_data': {
                    'position': EventStream(
                        topic='AMOR_metadata',
                        source='SQ:AMOR:motd:dvv.RBV',
                        mod='f142',
                        dtype='double',
                    ),
                    'units': 'mm',
                },
                'horizontal:NXevent_data': {
                    'position': EventStream(
                        topic='AMOR_metadata',
                        source='SQ:AMOR:motd:dvh.RBV',
                        mod='f142',
                        dtype='double',
                    ),
                    'units': 'mm',
                },
            },
            'middle focus:NXcollection': {
                'slot:NXevent_data': {
                    'position': EventStream(
                        topic='AMOR_metadata',
                        source='SQ:AMOR:motd:dmf.RBV',
                        mod='f142',
                        dtype='double',
                    ),
                    'units': 'mm',
                },
            },
        },
        'chopper:NXcollection': {
            'comment': 'Frequency means pulse frequency. The discs have 2 openings each.',
            'master:NXcollection': {
                'frequency:NXevent_data': {
                    'position': EventStream(
                        topic='AMOR_metadata',
                        source='SQ:AMOR:chopper:DCU1:Speed',
                        mod='f142',
                        dtype='double',
                    ),
                    'units': 'Hz',
                },
                'position:NXevent_data': {
                    'position': EventStream(
                        topic='AMOR_metadata',
                        source='SQ:AMOR:chopper:DCU1:Position',
                        mod='f142',
                        dtype='double',
                    ),
                    'units': 'deg',
                },
            },
            'slave:NXcollection': {
                'frequency:NXevent_data': {
                    'position': EventStream(
                        topic='AMOR_metadata',
                        source='SQ:AMOR:chopper:DCU2:Speed',
                        mod='f142',
                        dtype='double',
                    ),
                    'units': 'Hz',
                },
                'position:NXevent_data': {
                    'position': EventStream(
                        topic='AMOR_metadata',
                        source='SQ:AMOR:chopper:DCU2:Position',
                        mod='f142',
                        dtype='double',
                    ),
                    'units': 'deg',
                },
            },
        },
    },
    #     'user and data identifier:NXentry': {
    #         'owner': DeviceAttribute('Amor', 'responsible'),
    #         'facility': '<value>',
    #         'affiliation': None,
    #         'experiment ID': DeviceDataset('Exp', 'proposal'),
    #         'experiment date': '<value>',
    #         'title': DeviceDataset('Exp', 'title'),
    #     },
    'experiment:NXcollection': {
        # 'instrument': 'neutron reflectometer Amor',
        # 'probe': 'neutrons',
        # 'polarisation': '<value>',
        'measurement:NXcollection': {
            #     'scheme': 'angle- and energy-dispersive',
            #     'wavelength': {
            #         'min': '<value>',
            #         'max': '<value>',
            #         'resolution': {'type': 'prop', 'sigma': 0.02},
            #         'units': 'angstrom',
            #     },
            'angle:NXcollection': {
                'mu': DeviceDataset('mu', dtype='float'),
                'nu': DeviceDataset('nu', dtype='float'),
            },
            #     'count mode': {
            #         'mode': DeviceDataset('Exp', 'mode'),
            #         'preset': '<value>',
        },
        "title": DeviceDataset('Exp', 'title'),
        "user:NXuser": {
            "name": DeviceDataset('Exp', 'users'),
            "email": DeviceDataset('Exp', 'localcontact'),
        },
        "proposal_id": DeviceDataset('Exp', 'proposal'),
        "start_time": DeviceDataset('dataset', 'starttime'),
        "data:NXevent_data": {
            "data": EventStream(topic='FREIA_detector',
                                mod='ev42',
                                source='multiblade',
                                dtype='uint32'),
        },
        'proton_current:NXevent_data': {
            'value': EventStream(
                topic='AMOR_metadata',
                source='MHC6:IST:2',
                mod='f142',
                dtype='double',
            ),
            'units': 'mC',
        },

    },
}

_dv = 9999.9

amor_streaming = {
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
        "area_detector:NXData": {
            "data": NXLink('AMOR/area_detector'),
        },
        "AMOR:NXinstrument": {
            "name": "SINQ AMOR",
            "definition": NXDataset(
                'TOFNREF', dtype='string',
                url="http://www.neutron.anl.gov/nexus/xml/NXtofnref.xml"),
            "SINQ:NXSource": {
                "name": NXDataset('SINQ'),
                "type": NXDataset('Continuous flux spallation source')
            },
            "amor_mode": DeviceDataset('Exp', 'mode'),
            "chopper1:NXdisk_chopper": {
                "type": "Chopper type single",
                "rotation_speed:NXevent_data": {
                    'speed': EventStream(topic='AMOR_metadata',
                                         source='SQ:AMOR:chopper:DCU1:Speed',
                                         mod='f142',
                                         dtype='double', ),
                    'units': 'rpm',
                },
                "phase:NXevent_data": {
                    'phase': EventStream(topic='AMOR_metadata',
                                         source='SQ:AMOR:chopper:DCU1:Position',
                                         mod='f142',
                                         dtype='double', ),
                    'units': 'deg',
                },
                "distance": {},
            },
            "chopper2:NXdisk_chopper": {
                "type": "Chopper type single",
                "rotation_speed:NXevent_data": {
                    'speed': EventStream(topic='AMOR_metadata',
                                         source='SQ:AMOR:chopper:DCU2:Speed',
                                         mod='f142',
                                         dtype='double', ),
                    'units': 'Hz',
                },
                "phase:NXevent_data": {
                    'phase': EventStream(topic='AMOR_metadata',
                                         source='SQ:AMOR:chopper:DCU2:Position',
                                         mod='f142',
                                         dtype='double', ),
                    'units': 'deg',
                },
                "ratio:NXevent_data": {
                    'ratio': EventStream(topic='AMOR_metadata',
                                         source='SQ:AMOR:chopper:DCU2:Position',
                                         mod='f142',
                                         dtype='double', ),
                    'units': 'deg',
                },
                "distance": {},
            },
            "pre_sample_slit1:NXslit": {
                "bottom:NXevent_data": {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motd:d1b.RBV',
                                            mod='f142',
                                            dtype='double', ),
                    'units': 'mm',
                },
                "top:NXevent_data": {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motd:d1t.RBV',
                                            mod='f142',
                                            dtype='double', ),
                    'units': 'mm',
                },
                "left:NXevent_data": {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motd:d1l.RBV',
                                            mod='f142',
                                            dtype='double', ),
                    'units': 'mm',
                },
                "right:NXevent_data": {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motd:d1r.RBV',
                                            mod='f142',
                                            dtype='double', ),
                    'units': 'mm',
                },
                # "distance": NXDataset(
                #     DistancesPlaceholder('slit1', _dv),
                #     dtype='float'),
            },
            "pre_sample_slit2:NXslit": {
                "bottom:NXevent_data": {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motc:d2b.RBV',
                                            mod='f142',
                                            dtype='double', ),
                    'units': 'mm',
                },
                "top:NXevent_data": {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motc:d2t.RBV',
                                            mod='f142',
                                            dtype='double', ),
                    'units': 'mm',
                },
                "left:NXevent_data": {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motc:d2l.RBV',
                                            mod='f142',
                                            dtype='double', ),
                    'units': 'mm',
                },
                "right:NXevent_data": {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motc:d2r.RBV',
                                            mod='f142',
                                            dtype='double', ),
                    'units': 'mm',
                },
                # "distance": NXDataset(
                #     DistancesPlaceholder('slit2', _dv),
                #     dtype='float'),
            },
            'virtual_source:NXslit': {
                'vertical:NXevent_data': {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motd:dvv.RBV',
                                            mod='f142',
                                            dtype='int', ),
                    },
                'horizontal:NXevent_data': {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motd:dvh.RBV',
                                            mod='f142',
                                            dtype='int', ),
                    },
                'middle_focus:NXevent_data': {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motd:dmf.RBV',
                                            mod='f142',
                                            dtype='int', ),
                    },
            },
            # "polarizer:NXpolariser": {
            #     "spin_state": DeviceDataset('SpinFlipper',
            #                                 dtype='string')
            # },
            "detector:NXdetector": {
                # "chopper_detector_distance": NXDataset(
                #     ComponentDistancePlaceholder('chopper',
                #                                  'detector'),
                #     dtype='float'),
                "acquisition_mode": "event",
                "distance": NXDataset(
                    DistancesPlaceholder('detector', _dv),
                    dtype='float'),
                "polar_angle:NXevent_data": {
                    'position': EventStream(topic='AMOR_metadata',
                                            source='SQ:AMOR:motc:s2t.RBV',
                                            mod='f142',
                                            dtype='double', ),
                    'units': 'deg',
                },
                "data:NXevent_data": {
                    "data": EventStream(topic='FREIA_detector',
                                        mod='ev42',
                                        source='multiblade',
                                        dtype='uint32'),
                },
                'proton_current:NXevent_data': {
                    'value': EventStream(topic='AMOR_metadata',
                                         source='MHC6:IST:2',
                                         mod='f142',
                                         dtype='double', ),
                    'units': 'mC',
                },
                # "x_pixel_size": "",
                # "y_pixel_size": "",
                "count_time":"",
                "depends_on": "transformation/distance",
                "transformation:NXtransformations": {
                    "distance:NXevent_data": {
                        'vector': (0, 0, 1),
                        'attributes': '',
                        'depends_on': 'height',
                        'transformation_type': 'translation',
                        'value': EventStream(topic='AMOR_metadata',
                                                source='SQ:AMOR:motc:cox.RBV',
                                                mod='f142',
                                                dtype='double', ),
                        'units': 'mm', },
                    "height:NXevent_data": {
                        'vector': (0, 1, 0),
                        'attributes': '',
                        'depends_on': 'rotation',
                        'transformation_type': 'translation',
                        'value': EventStream(topic='AMOR_metadata',
                                                source='SQ:AMOR:motc:coz.RBV',
                                                mod='f142',
                                                dtype='double', ),
                        'units': 'mm', },
                    "rotation:NXevent_data": {
                        'vector': (1, 0, 0),
                        'attributes': '',
                        'depends_on': '.',
                        'transformation_type': 'rotation',
                        'value': EventStream(topic='AMOR_metadata',
                                                source='SQ:AMOR:motc:com.RBV',
                                                mod='f142',
                                                dtype='double', ),
                        'units': 'deg', },
                }
            },
            "sample:NXsample": {
                "name": DeviceDataset('Sample', 'samplename'),
                "distance": NXDataset(
                    DistancesPlaceholder('sample', 0), 'float'),
                "base_height": "",
                "chi": "",
                "temperature": "",
                "magnetic_field": "",
                "x_translation": 0,
                "depends_on": "transformation/height",
                "transformation:NXtransformations": {
                    "height:NXevent_data": {
                        'offset': '', # stz
                        'vector': (0, 1, 0),
                        'attributes': '',
                        'depends_on': 'rotation',
                        'transformation_type': 'translation',
                        'value': EventStream(topic='AMOR_metadata',
                                             source='SQ:AMOR:motc:soz.RBV',
                                             mod='f142',
                                             dtype='double', ),
                        'units': 'mm', },
                    "rotation:NXevent_data": {
                        'vector': (1, 0, 0),
                        'attributes': '',
                        'depends_on': '.',
                        'transformation_type': 'rotation',
                        'value': EventStream(topic='AMOR_metadata',
                                             source='SQ:AMOR:motc:som.RBV',
                                             mod='f142',
                                             dtype='double', ),
                        'units': 'deg', },
                }
            }
        }
    }
}
