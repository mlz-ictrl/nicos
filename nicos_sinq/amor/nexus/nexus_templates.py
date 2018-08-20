from nicos_ess.nexus import DeviceAttribute, NXDataset, DeviceDataset, \
    DeviceStream
from nicos_sinq.amor.nexus.elements import HistogramStream
from nicos_sinq.amor.nexus.placeholder import SlitGeometryPlaceholder, \
    SlitValuePlaceholder

# Default template for AMOR including most of the devices
amor_default = {
    "NeXus_Version": "4.3.0",
    "instrument": "AMOR",
    "owner": DeviceAttribute('Amor', 'responsible'),
    "entry1:NXentry": {
        "comment": DeviceDataset('Exp', 'remark'),
        "title": DeviceDataset('Exp', 'title'),
        "amor_mode": DeviceDataset('Exp', 'mode'),
        "user:NXuser": {
            "name": DeviceDataset('Exp', 'users'),
            "email": DeviceDataset('Exp', 'localcontact')
        },
        "sample:NXsample": {
            "name": DeviceDataset('Sample', 'samplename'),
            "distance": DeviceDataset('Distances', 'sample'),
            "base_height": DeviceDataset('stz'),
            "chi": DeviceDataset('sch'),
            "omega_height": DeviceDataset('soz'),
            "rotation": DeviceDataset('som'),
            "magnetic_field": DeviceDataset('hsy')
        },
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
                "chopper_phase": DeviceDataset('ch1', 'phase', 'float64'),
                "rotation_speed": DeviceDataset('ch1', 'speed', units='rpm'),
                "distance": DeviceDataset('Distances', 'chopper')
            },
            "after_sample1:NXaperture": {
                "bottom": NXDataset(SlitValuePlaceholder('slit4', 'bottom')),
                "top": NXDataset(SlitValuePlaceholder('slit4', 'top')),
                "left": NXDataset(SlitValuePlaceholder('slit4', 'left')),
                "right": NXDataset(SlitValuePlaceholder('slit4', 'right')),
                "distance": DeviceDataset('Distances', 'slit4'),
                "geometry:NXgeometry": {
                    "shape:NXshape": {
                        "size": NXDataset(SlitGeometryPlaceholder(4))
                    }
                }
            },
            "analyzer:NXfilter": {
                "distance": DeviceDataset('Distances', 'analyser'),
                "height": DeviceDataset('atz'),
                "omega_height": DeviceDataset('aoz'),
                "rotation": DeviceDataset('aom'),
                "spin_state": DeviceDataset('aby', 'state', 'string')
            },
            "area_detector:NXdetector": {
                "chopper_detector_distance": NXDataset(8980.0),
                "distance": DeviceDataset('Distances', 'detector'),
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
                    source="area.tof",)
            },
            'single_detector_1:NXdetector': {
                "data": HistogramStream(
                    detector='psd_tof',
                    channel='single_det1',
                    dataset_names=['time_binning'],
                    topic="AMOR_singleDetector1",
                    source="single.tof",)
            },
            'single_detector_2:NXdetector': {
                "data": HistogramStream(
                    detector='psd_tof',
                    channel='single_det2',
                    dataset_names=['time_binning'],
                    topic="AMOR_singleDetector2",
                    source="single.tof",)
            },
            "control:NXmonitor": {
                "mode": DeviceDataset('psd_tof', 'mode', 'string'),
                "preset": DeviceDataset('psd_tof', 'preset'),
                "monitor1": DeviceStream('monitorval'),
                "monitor2": DeviceStream('protoncurr')
            },
            "detector_slit:NXaperture": {
                "height": NXDataset(SlitValuePlaceholder('slit5',
                                                         'horizontal')),
                "width": NXDataset(SlitValuePlaceholder('slit5', 'vertical')),
            },
            "frame_overlap_mirror:NXmirror": {
                "distance": DeviceDataset('Distances', 'filter'),
                "height": DeviceDataset('ftz'),
                "omgea": DeviceDataset('fom')
            },
            "polarizer:NXpolariser": {
                "distance": DeviceDataset('Distances', 'polariser'),
                "height": DeviceDataset('mtz'),
                "magnet_current": DeviceDataset('pby'),
                "omega_height": DeviceDataset('moz'),
                "rotation": DeviceDataset('mom'),
                "spin_state": DeviceDataset('pby', 'state', 'string'),
                "y_translation": DeviceDataset('mty')
            },
            "pre_sample_slit1:NXaperture": {
                "bottom": NXDataset(SlitValuePlaceholder('slit1', 'bottom')),
                "top": NXDataset(SlitValuePlaceholder('slit1', 'top')),
                "left": NXDataset(SlitValuePlaceholder('slit1', 'left')),
                "right": NXDataset(SlitValuePlaceholder('slit1', 'right')),
                "distance": DeviceDataset('Distances', 'slit1'),
                "geometry:NXgeometry": {
                    "shape:NXshape": {
                        "size": NXDataset(SlitGeometryPlaceholder(1))
                    }
                }
            },
            "pre_sample_slit2:NXaperture": {
                "bottom": NXDataset(SlitValuePlaceholder('slit2', 'bottom')),
                "top": NXDataset(SlitValuePlaceholder('slit2', 'top')),
                "left": NXDataset(SlitValuePlaceholder('slit2', 'left')),
                "right": NXDataset(SlitValuePlaceholder('slit2', 'right')),
                "distance": DeviceDataset('Distances', 'slit2'),
                "geometry:NXgeometry": {
                    "shape:NXshape": {
                        "size": NXDataset(SlitGeometryPlaceholder(2))
                    }
                }
            },
            "pre_sample_slit3:NXaperture": {
                "bottom": NXDataset(SlitValuePlaceholder('slit3', 'bottom')),
                "top": NXDataset(SlitValuePlaceholder('slit3', 'top')),
                "left": NXDataset(SlitValuePlaceholder('slit3', 'left')),
                "right": NXDataset(SlitValuePlaceholder('slit3', 'right')),
                "distance": DeviceDataset('Distances', 'slit3'),
                "geometry:NXgeometry": {
                    "shape:NXshape": {
                        "size": NXDataset(SlitGeometryPlaceholder(3))
                    }
                }
            },
            "slave_chopper:NXchopper": {
                "chopper_phase": DeviceDataset('ch2', 'phase'),
                "rotation_speed": DeviceDataset('ch2', 'speed'),
                "distance": DeviceDataset('Distances', 'chopper')
            }
        },

    }
}

# Template that saves only the detector data
detector_only = {
    "entry1:NXentry": {
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

# Template that saves only the sample data
sample_only = {
    "entry1:NXentry": {
        "sample:NXsample": {
            "name": DeviceDataset('Sample', 'samplename'),
            "distance": NXDataset(0.0),
            "base_height": DeviceDataset('stz'),
            "chi": DeviceDataset('sch'),
            "omega_height": DeviceDataset('soz'),
            "rotation": DeviceDataset('som'),
            "magnetic_field": DeviceDataset('hsy')
        },
    },
}
