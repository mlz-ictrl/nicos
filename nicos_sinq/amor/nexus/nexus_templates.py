from nicos_ess.nexus import DeviceAttribute, NXDataset, DeviceDataset, \
    DeviceStream, EventStream
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
                "x_detector": NXDataset(
                    [-86, -84.6562, -83.3125, -81.9688, -80.625, -79.2812,
                     -77.9375, -76.5938, -75.25, -73.9062, -72.5625, -71.2188,
                     -69.875, -68.5312, -67.1875, -65.8438, -64.5, -63.1562,
                     -61.8125, -60.4688, -59.125, -57.7812, -56.4375, -55.0938,
                     -53.75, -52.4062, -51.0625, -49.7188, -48.375, -47.0312,
                     -45.6875, -44.3438, -43, -41.6562, -40.3125, -38.9688,
                     -37.625, -36.2812, -34.9375, -33.5938, -32.25, -30.9062,
                     -29.5625, -28.2188, -26.875, -25.5312, -24.1875, -22.8438,
                     -21.5, -20.1562, -18.8125, -17.4688, -16.125, -14.7812,
                     -13.4375, -12.0938, -10.75, -9.40625, -8.0625, -6.71875,
                     -5.375, -4.03125, -2.6875, -1.34375, 0, 1.34375, 2.6875,
                     4.03125, 5.375, 6.71875, 8.0625, 9.40625, 10.75, 12.0938,
                     13.4375, 14.7812, 16.125, 17.4688, 18.8125, 20.1562, 21.5,
                     22.8438, 24.1875, 25.5312, 26.875, 28.2188, 29.5625,
                     30.9062, 32.25, 33.5938, 34.9375, 36.2812, 37.625,
                     38.9688, 40.3125, 41.6562, 43, 44.3438, 45.6875, 47.0312,
                     48.375, 49.7188, 51.0625, 52.4062, 53.75, 55.0938,
                     56.4375, 57.7812, 59.125, 60.4688, 61.8125, 63.1562, 64.5,
                     65.8438, 67.1875, 68.5312, 69.875, 71.2188, 72.5625,
                     73.9062, 75.25, 76.5938, 77.9375, 79.2812, 80.625,
                     81.9688, 83.3125, 84.6562
                     ], dtype='float', axis=2, units='mm'),
                "y_detector": NXDataset(
                    [-95, -94.2578, -93.5156, -92.7734, -92.0312, -91.2891,
                     -90.5469, -89.8047, -89.0625, -88.3203, -87.5781,
                     -86.8359, -86.0938, -85.3516, -84.6094, -83.8672, -83.125,
                     -82.3828, -81.6406, -80.8984, -80.1562, -79.4141,
                     -78.6719, -77.9297, -77.1875, -76.4453, -75.7031,
                     -74.9609, -74.2188, -73.4766, -72.7344, -71.9922, -71.25,
                     -70.5078, -69.7656, -69.0234, -68.2812, -67.5391,
                     -66.7969, -66.0547, -65.3125, -64.5703, -63.8281,
                     -63.0859, -62.3438, -61.6016, -60.8594, -60.1172, -59.375,
                     -58.6328, -57.8906, -57.1484, -56.4062, -55.6641,
                     -54.9219, -54.1797, -53.4375, -52.6953, -51.9531,
                     -51.2109, -50.4688, -49.7266, -48.9844, -48.2422, -47.5,
                     -46.7578, -46.0156, -45.2734, -44.5312, -43.7891,
                     -43.0469, -42.3047, -41.5625, -40.8203, -40.0781,
                     -39.3359, -38.5938, -37.8516, -37.1094, -36.3672, -35.625,
                     -34.8828, -34.1406, -33.3984, -32.6562, -31.9141,
                     -31.1719, -30.4297, -29.6875, -28.9453, -28.2031,
                     -27.4609, -26.7188, -25.9766, -25.2344, -24.4922, -23.75,
                     -23.0078, -22.2656, -21.5234, -20.7812, -20.0391,
                     -19.2969, -18.5547, -17.8125, -17.0703, -16.3281,
                     -15.5859, -14.8438, -14.1016, -13.3594, -12.6172, -11.875,
                     -11.1328, -10.3906, -9.64844, -8.90625, -8.16406,
                     -7.42188, -6.67969, -5.9375, -5.19531, -4.45312, -3.71094,
                     -2.96875, -2.22656, -1.48438, -0.742188, 0, 0.742188,
                     1.48438, 2.22656, 2.96875, 3.71094, 4.45312, 5.19531,
                     5.9375, 6.67969, 7.42188, 8.16406, 8.90625, 9.64844,
                     10.3906, 11.1328, 11.875, 12.6172, 13.3594, 14.1016,
                     14.8438, 15.5859, 16.3281, 17.0703, 17.8125, 18.5547,
                     19.2969, 20.0391, 20.7812, 21.5234, 22.2656, 23.0078,
                     23.75, 24.4922, 25.2344, 25.9766, 26.7188, 27.4609,
                     28.2031, 28.9453, 29.6875, 30.4297, 31.1719, 31.9141,
                     32.6562, 33.3984, 34.1406, 34.8828, 35.625, 36.3672,
                     37.1094, 37.8516, 38.5938, 39.3359, 40.0781, 40.8203,
                     41.5625, 42.3047, 43.0469, 43.7891, 44.5312, 45.2734,
                     46.0156, 46.7578, 47.5, 48.2422, 48.9844, 49.7266,
                     50.4688, 51.2109, 51.9531, 52.6953, 53.4375, 54.1797,
                     54.9219, 55.6641, 56.4062, 57.1484, 57.8906, 58.6328,
                     59.375, 60.1172, 60.8594, 61.6016, 62.3438, 63.0859,
                     63.8281, 64.5703, 65.3125, 66.0547, 66.7969, 67.5391,
                     68.2812, 69.0234, 69.7656, 70.5078, 71.25, 71.9922,
                     72.7344, 73.4766, 74.2188, 74.9609, 75.7031, 76.4453,
                     77.1875, 77.9297, 78.6719, 79.4141, 80.1562, 80.8984,
                     81.6406, 82.3828, 83.125, 83.8672, 84.6094, 85.3516,
                     86.0938, 86.8359, 87.5781, 88.3203, 89.0625, 89.8047,
                     90.5469, 91.2891, 92.0312, 92.7734, 93.5156, 94.2578
                     ], dtype='float', axis=1, units='mm'),
                "data": EventStream(topic="AMOR.area.detector",
                                    source="AMOR.event.stream",
                                    broker="localhost:9092",
                                    dtype="uint32")
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
                "data": EventStream("AMOR.area.detector", "AMOR.event.stream",
                                    "localhost:9092")
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
