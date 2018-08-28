from nicos_ess.nexus import DeviceAttribute, NXDataset, DeviceDataset, NXLink
from nicos_sinq.amor.nexus.elements import HistogramStream
from nicos_sinq.amor.nexus.placeholder import SlitGeometryPlaceholder, \
    UserEmailPlaceholder, ComponentDistancePlaceholder, \
    TimeBinningPlaceholder, DistancesPlaceholder

_dv = 9999.9

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
        "sample:NXsample": {
            "name": DeviceDataset('Sample', 'samplename'),
            "distance": NXDataset(DistancesPlaceholder('sample', _dv), 'float'),
            "base_height": DeviceDataset('stz', dtype='float'),
            "chi": DeviceDataset('sch', dtype='float'),
            "omega_height": DeviceDataset('soz', dtype='float'),
            "rotation": DeviceDataset('som', dtype='float'),
            "magnetic_field": DeviceDataset('hsy', dtype='float')
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
            },
            "T0_chopper:NXdisk_chopper": {
                "chopper_phase": DeviceDataset('ch1', 'phase', 'float'),
                "rotation_speed": DeviceDataset('ch1', 'speed', dtype='float',
                                                units='rpm'),
                "distance": NXDataset(DistancesPlaceholder('chopper', _dv), dtype='float')
            },
            "after_sample1:NXaperture": {
                "bottom": DeviceDataset('d4b', defaultval=_dv, dtype='float'),
                "top": DeviceDataset('d4t', defaultval=_dv, dtype='float'),
                "left": DeviceDataset('d1l', defaultval=_dv, dtype='float'),
                "right": DeviceDataset('d1r', defaultval=_dv, dtype='float'),
                "distance": NXDataset(DistancesPlaceholder('slit4', _dv), dtype='float'),
                "geometry:NXgeometry": {
                    "shape:NXshape": {
                        "size": NXDataset(SlitGeometryPlaceholder(4, _dv), dtype='float')
                    }
                }
            },
            "analyzer:NXfilter": {
                "distance": NXDataset(DistancesPlaceholder('analyser', _dv), dtype='float'),
                "height": DeviceDataset('atz', defaultval=_dv, dtype='float'),
                "omega_height": DeviceDataset('aoz', defaultval=_dv, dtype='float'),
                "rotation": DeviceDataset('aom', defaultval=_dv, dtype='float'),
            },
            "area_detector:NXdetector": {
                "chopper_detector_distance": NXDataset(
                    ComponentDistancePlaceholder('chopper', 'detector'), dtype='float'),
                "distance": NXDataset(DistancesPlaceholder('detector', _dv), dtype='float'),
                "height": DeviceDataset('coz', dtype='float'),
                "rotation": DeviceDataset('com', dtype='float'),
                "detector_rotation_offset": DeviceDataset('com', 'offset', dtype='float'),
                "polar_angle": DeviceDataset('s2t', dtype='float'),
                "x_position": DeviceDataset('cox', dtype='float'),
                "time_binning": NXDataset(
                    TimeBinningPlaceholder('psd_tof', 'area_detector', 2),
                    dtype='float', axis=3, units='ms'),
                "data": HistogramStream(
                    detector='psd_tof',
                    channel='area_detector',
                    dataset_names=['x_detector', 'y_detector', 'time_binning_orig'],
                    topic="AMOR_areaDetector",
                    source="area.tof",)
            },
            'single_detector_1:NXdetector': {
                "time_binning": NXDataset(
                    TimeBinningPlaceholder('psd_tof', 'single_det1', 0),
                    dtype='float', axis=1, units='ms'),
                "data": HistogramStream(
                    detector='psd_tof',
                    channel='single_det1',
                    dataset_names=['time_binning_orig'],
                    topic="AMOR_singleDetector1",
                    source="single.tof",)
            },
            'single_detector_2:NXdetector': {
                "time_binning": NXDataset(
                    TimeBinningPlaceholder('psd_tof', 'single_det2', 0),
                    dtype='float', axis=1, units='ms'),
                "data": HistogramStream(
                    detector='psd_tof',
                    channel='single_det2',
                    dataset_names=['time_binning_orig'],
                    topic="AMOR_singleDetector2",
                    source="single.tof",)
            },
            "control:NXmonitor": {
                "count_mode": DeviceDataset('psd_tof', 'mode', 'string'),
                "preset": DeviceDataset('psd_tof', 'preset', dtype='float'),
            },
            "detector_slit:NXaperture": {
                "height": DeviceDataset('d5h', defaultval=_dv, type='float'),
                "width": DeviceDataset('d5v', defaultval=_dv, dtype='float'),
            },
            "frame_overlap_mirror:NXmirror": {
                "distance": NXDataset(DistancesPlaceholder('filter', _dv), dtype='float'),
                "height": DeviceDataset('ftz', dtype='float'),
                "omgea": DeviceDataset('fom', dtype='float')
            },
            "polarizer:NXpolariser": {
                "distance": NXDataset(DistancesPlaceholder('polariser', _dv), dtype='float'),
                "height": DeviceDataset('mtz', defaultval=_dv, dtype='float'),
                "omega_height": DeviceDataset('moz', defaultval=_dv, dtype='float'),
                "rotation": DeviceDataset('mom', defaultval=_dv, dtype='float'),
                "y_translation": DeviceDataset('mty', defaultval=_dv, dtype='float'),
                "spin_state": DeviceDataset('SpinFlipper', dtype='string')
            },
            "pre_sample_slit1:NXaperture": {
                "bottom": DeviceDataset('d1b', defaultval=_dv, dtype='float'),
                "top": DeviceDataset('d1t', defaultval=_dv, dtype='float'),
                "left": DeviceDataset('d1l', defaultval=_dv, dtype='float'),
                "right": DeviceDataset('d1r', defaultval=_dv, dtype='float'),
                "distance": NXDataset(DistancesPlaceholder('slit1', _dv), dtype='float'),
                "geometry:NXgeometry": {
                    "shape:NXshape": {
                        "size": NXDataset(SlitGeometryPlaceholder(1, _dv), dtype='float')
                    }
                }
            },
            "pre_sample_slit2:NXaperture": {
                "bottom": DeviceDataset('d2b', defaultval=_dv, dtype='float'),
                "top": DeviceDataset('d2t', defaultval=_dv, dtype='float'),
                "left": DeviceDataset('d1l', defaultval=_dv, dtype='float'),
                "right": DeviceDataset('d1r', defaultval=_dv, dtype='float'),
                "distance": NXDataset(DistancesPlaceholder('slit2', _dv), dtype='float'),
                "geometry:NXgeometry": {
                    "shape:NXshape": {
                        "size": NXDataset(SlitGeometryPlaceholder(2, _dv), dtype='float')
                    }
                }
            },
            "pre_sample_slit3:NXaperture": {
                "bottom": DeviceDataset('d3b', defaultval=_dv, dtype='float'),
                "top": DeviceDataset('d3t', defaultval=_dv, dtype='float'),
                "left": DeviceDataset('d1l', defaultval=_dv, dtype='float'),
                "right": DeviceDataset('d1r', defaultval=_dv, dtype='float'),
                "distance": NXDataset(DistancesPlaceholder('slit3', _dv), dtype='float'),
                "geometry:NXgeometry": {
                    "shape:NXshape": {
                        "size": NXDataset(SlitGeometryPlaceholder(3, _dv), dtype='float')
                    }
                }
            },
            "slave_chopper:NXchopper": {
                "chopper_phase": DeviceDataset('ch2', 'phase', dtype='float'),
                "rotation_speed": DeviceDataset('ch2', 'speed', dtype='float'),
                "distance": NXDataset(DistancesPlaceholder('chopper', _dv), dtype='float'),
            }
        },

    }
}

# Template that saves only the detector data
detector_only = {
    "entry1:NXentry": {
        "area_detector": NXLink('AMOR/area_detector'),
        "AMOR:NXinstrument": {
            "name": DeviceAttribute("Amor", "instrument"),
            "area_detector:NXdetector": {
                "chopper_detector_distance": NXDataset(8980.0),
                "distance": DeviceDataset('ddetector'),
                "height": DeviceDataset('coz'),
                "rotation": DeviceDataset('com'),
                "detector_rotation_offset": DeviceDataset('com', 'offset'),
                "polar_angle": DeviceDataset('s2t'),
                "x_position": DeviceDataset('cox'),
                "data": HistogramStream(
                    detector='psd_tof',
                    channel='area_detector',
                    dataset_names=['x_detector', 'y_detector', 'time_binning'],
                    topic="AMOR_areaDetector",
                    source="area.tof")
            },
            'single_detector_1:NXdetector': {
                "data": HistogramStream(
                    detector='psd_tof',
                    channel='single_det1',
                    dataset_names=['time_binning'],
                    topic="AMOR_singleDetector1",
                    source="single.tof")
            },
            'single_detector_2:NXdetector': {
                "data": HistogramStream(
                    detector='psd_tof',
                    channel='single_det2',
                    dataset_names=['time_binning'],
                    topic="AMOR_singleDetector2",
                    source="single.tof")
            },
        },
    }
}

sample_only = {
    "entry1:NXentry": {
        "sample:NXsample": {
            "name": DeviceDataset('Sample', 'samplename'),
            "distance": DeviceDataset('Distances', 'sample', 'float'),
            "base_height": DeviceDataset('stz', dtype='float'),
            "chi": DeviceDataset('sch', dtype='float'),
            "omega_height": DeviceDataset('soz', dtype='float'),
            "rotation": DeviceDataset('som', dtype='float'),
            "magnetic_field": DeviceDataset('hsy', dtype='float')
        },
    }
}
