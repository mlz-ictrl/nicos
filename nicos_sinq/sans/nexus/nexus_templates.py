from copy import deepcopy

from nicos import session
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, ImageDataset, NexusSampleEnv, \
    NXAttribute, NXLink, NXScanLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_sinq.nexus.specialelements import FixedArray

sans_detector = {
        "count_mode": DetectorDataset("mode", "string"),
        "counting_time": DetectorDataset("elapsedtime", "float32",
                                         units=NXAttribute("seconds",
                                                           "string")),
        "preset": DetectorDataset("preset", "float32"),
        "x_position": DeviceDataset("detx"),
        "x_null": DeviceDataset("detx", "offset"),
        "y_position": DeviceDataset("dety"),
        "y_null": DeviceDataset("dety", "offset"),
        "chi_position": DeviceDataset("detphi"),
        "detector_x": FixedArray(-64, 1, 128),
        "detector_y": FixedArray(-64, 1, 128),
        "counts": ImageDataset(0, 0, signal=NXAttribute(1, "int32")),
        "data": NXLink("/entry1/SANS/detector/counts"),
        "distance": NXLink("/entry1/SANS/detector/x_position"),
        "x_pixel_size": ConstDataset(7.5, "float",
                                     units=NXAttribute("mm", "string")),
        "y_pixel_size": ConstDataset(7.5, "float",
                                     units=NXAttribute("mm", "string")),
        "polar_angle": ConstDataset(0, "float",
                                    units=NXAttribute("degree", "string")),
        "aequatorial_angle": ConstDataset(0, "float",
                                          units=NXAttribute("degree",
                                                            "string")),
        "azimuthal_angle": ConstDataset(0, "float",
                                        units=NXAttribute("degree", "string")),
        "rotation_angle": NXLink("/entry1/SANS/detector/chi_position"),
        "beam_center_x": ConstDataset(0, "float",
                                      units=NXAttribute("degree", "string")),
        "beam_center_y": ConstDataset(0, "float", units=NXAttribute("degree",
                                                                    "string"))
}

sans_default = {"NeXus_Version": "4.4.0",
                "instrument": "SANS at SINQ",
                "owner": DeviceAttribute("SANS", "responsible"),
                "entry1:NXentry": {
                    "title": DeviceDataset("Exp", "title"),
                    "proposal_title": DeviceDataset("Exp", "title"),
                    "proposal_id": DeviceDataset("Exp", "proposal"),
                    "start_time": NXTime(),
                    "end_time": NXTime(),
                    "definition": ConstDataset("NXsas", "string"),
                    "user:NXuser": {
                        "name": DeviceDataset("Exp", "users"),
                        "email": DeviceDataset("Exp", "localcontact")
                    },
                    "proposal_user:NXuser": {
                        "name": DeviceDataset("Exp", "users"),
                    },
                    "SANS:NXinstrument": {
                        "name": ConstDataset("SANS", "string"),
                        "Dornier-VS:NXchopper": {
                            "type": ConstDataset("Dornier Velocity Selector",
                                                 "string"),
                            "lambda": DeviceDataset("vs_lambda"),
                            "rotation_speed": DeviceDataset("vs_speed"),
                            "tilt": DeviceDataset("vs_tilt"),
                        },
                        "monochromator:NXmonochromator": {
                          "wavelength": NXLink(
                              "/entry1/SANS/Dornier-VS/lambda"),
                          "wavelength_spread": ConstDataset(.2, "float"),
                        },
                        "SINQ:NXsource": {
                            "name": ConstDataset(
                                "SINQ, Paul Scherrer Institute", "string"),
                            "type": ConstDataset(
                                "continuous flux spallation source", "string"),
                            "probe": ConstDataset("neutron", "string"),
                        },
                        "attenuator:NXAttenuator": {
                            "selection": DeviceDataset("att"),
                        },
                        "beam_stop:NXstop": {
                            "x_position": DeviceDataset("bsx"),
                            "x_null": DeviceDataset("bsx", "offset"),
                            "y_position": DeviceDataset("bsy"),
                            "y_null": DeviceDataset("bsy", "offset"),
                            "out_flag": DeviceDataset("bsc"),
                        },
                        "collimator:NXcollimator": {
                            "length": DeviceDataset("coll"),
                            "geometry:NXgeometry": {
                                "shape:NXshape": {
                                    "shape":  ConstDataset(
                                        "nxcylinder", "string"),
                                },
                                "size": NXLink(
                                    "/entry1/SANS/collimator/length"),
                            }
                        },
                        "monitor1:NXmonitor": {
                            "counts": DetectorDataset("monitor1", "int32",
                                                      units=NXAttribute(
                                                                  "counts",
                                                                  "string")),
                        },
                        "monitor2:NXmonitor": {
                            "counts": DetectorDataset("monitor2", "int32",
                                                      units=NXAttribute(
                                                                  "counts",
                                                                  "string")),
                        },
                        "monitor3:NXmonitor": {
                            "counts": DetectorDataset("monitor3", "int32",
                                                      units=NXAttribute(
                                                                  "counts",
                                                                  "string")),
                        },
                        "monitor_5:NXmonitor": {
                            "counts": DetectorDataset("protoncount", "int32",
                                                      units=NXAttribute(
                                                                  "counts",
                                                                  "string")),
                        },
                        "monitor_7:NXmonitor": {
                            "counts": DetectorDataset("monitor7", "int32",
                                                      units=NXAttribute(
                                                                  "counts",
                                                                  "string")),
                        },
                        "monitor_8:NXmonitor": {
                            "counts": DetectorDataset("monitor8", "int32",
                                                      units=NXAttribute(
                                                                  "counts",
                                                                  "string")),
                        },
                        "integrated_beam:NXmonitor": {
                            "counts": DetectorDataset("protoncount", "int32",
                                                      units=NXAttribute(
                                                                  "counts",
                                                                  "string")),
                        },
                        "polarizer:NXpolarizer": {
                            "state": DeviceDataset("pol"),
                        }
                    },  # instrument
                    "control:NXmonitor": {
                        "preset": DetectorDataset("preset", "float32"),
                        "mode": DetectorDataset("mode", "string"),
                        "integral": DetectorDataset("monitor1", "int32",
                                                    units=NXAttribute(
                                                                    "counts",
                                                                    "string")),
                    },
                    "data1:NXdata": {
                        "counts": NXLink("/entry1/SANS/detector/counts"),
                        "data": NXLink("/entry1/SANS/detector/counts"),
                        "detector_x": NXLink(
                            "/entry1/SANS/detector/detector_x"),
                        "detector_y": NXLink(
                            "/entry1/SANS/detector/detector_y"),
                        "lambda": NXLink("/entry1/SANS/Dornier-VS/lambda"),
                        "None": NXScanLink(),
                    },
                }  # entry
                }  # root

sample_common = {
    "name": DeviceDataset("Sample", "samplename"),
    "hugo": NexusSampleEnv(),
    "temperature": DeviceDataset("temperature", "value", defaultval=0.0),
    "magfield": DeviceDataset("magfield", "value", defaultval=0.0),
    "aequatorial_angle": ConstDataset(0, "float",
                                      units=NXAttribute("degree", "string")),
}

sample_std = {
    "x_position": DeviceDataset("xo"),
    "x_null": DeviceDataset("xo", "offset"),
    "x_position_lower": DeviceDataset("xu"),
    "x_null_lower": DeviceDataset("xu", "offset"),
    "y_position": DeviceDataset("yo"),
    "y_null": DeviceDataset("yo", "offset"),
    "z_position": DeviceDataset("z"),
    "z_null": DeviceDataset("z", "offset"),
    "omega": DeviceDataset("sg"),
    "omega_null": DeviceDataset("sg", "offset"),
    "position": DeviceDataset("spos"),
    "position_null": DeviceDataset("spos", "offset"),
}

sample_magnet = {
    "magnet_omega": DeviceDataset("mom"),
    "magnet_omega_null": DeviceDataset("mom", "offset"),
    "magnet_z": DeviceDataset("mz"),
    "magnet_z_null": DeviceDataset("mz", "offset"),
}


class SANSTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        full = deepcopy(sans_default)
        full["entry1:NXentry"]["SANS:NXinstrument"]["detector:NXdetector"] =\
            deepcopy(sans_detector)
        if "sample" in session.loaded_setups:
            full["entry1:NXentry"]["sample:NXsample"] = \
                dict(sample_common, **sample_std)
        elif "emagnet_sample" in session.loaded_setups:
            full["entry1:NXentry"]["sample:NXsample"] = \
                dict(sample_common, **sample_magnet)
        else:
            full["entry1:NXentry"]["sample:NXsample"] = sample_common
        return full
