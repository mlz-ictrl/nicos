# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#  Mark Koennecke <make.koennecke@psi.ch>
#  Jochen Stahn <jochen.stahn@psi.ch>
#
# *****************************************************************************

from nicos_ess.nexus import DeviceAttribute, DeviceDataset, EventStream, \
    NXDataset, NXLink
from nicos_sinq.amor.nexus.placeholder import UserEmailPlaceholder

# chopper settings
_ch1_sp = 500
_ch2_ph = -12.5

metaMod = "f144"
metaTopic = "AMOR_nicosForwarder"

amor_streaming = {
    "NeXus_Version": "4.3.0",
    "instrument": "Amor",
    "owner": DeviceAttribute("Amor", "responsible"),
    "entry1:NXentry": {
        # ownership and origin
        "title": DeviceDataset("Exp", "title"),
        "user:NXuser": {
            "name": NXDataset(UserEmailPlaceholder("Exp", "users", False)),
            "email": NXDataset(UserEmailPlaceholder("Exp", "users", True)),
            "role": NXDataset("principal_investigator", dtype="string"),
        },
        "proposal_id": DeviceDataset("Exp", "proposal"),
        "start_time": DeviceDataset("dataset", "starttime"),
        "comment": DeviceDataset("Exp", "remark"),
        # measurement data
        "area_detector:NXData": {
            "data": NXLink("/entry1/Amor/detector/data"),
        },
        # experimental configuration
        "Amor:NXinstrument": {
            # general instrument info
            "name": NXDataset("Amor", dtype="string"),
            "definition": NXDataset(
                "TOFNREF", dtype="string",
                url="http://www.neutron.anl.gov/nexus/xml/NXtofnref.xml"),
            # source
            "source:NXSource": {
                "name": NXDataset("SINQ", dtype="string"),
                "type": NXDataset("Continuous flux spallation source",
                                  dtype="string"),
                "probe": NXDataset("neutron", dtype="string"),
            },
            "amor_mode": DeviceDataset("amormode"),
            # master parameters
            "master_parameters:NXcollection": {
                "description:NXcollection": {
                    "mu": NXDataset("Angle between instrument horizon and"
                                    " sample surface"),
                    "nu": NXDataset("Angle between instrument horizon and"
                                    " sample-detector"),
                    "kap": NXDataset("Angle between instrument horizon"
                                     " and beam center at the sample."
                                     " Depends on the deflector angle 'lom'"
                                     " and the first diaphragm vertical "
                                     " opening."),
                    "div": NXDataset("Vertical divergence of the beam incident"
                                     " on the sample. Defined by the first"
                                     " diaphragm vertical opening."),
                    "kad": NXDataset("Offset of the actual beam center with "
                                     " respect to full beam center. Defined"
                                     " by the first diaphragm vertical opening"
                                     " and probably by the deflector position"
                                     " 'ltz' and angle 'lom'."),
                },
                "mu:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="mu",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "deg",
                },
                "nu:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="nu",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "deg",
                },
                "kap:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="kap",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "deg",
                },
                "kad:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="kad",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "deg",
                },
                "div:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="div",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "deg",
                },
            },
            # beam line components
            # diaphragms
            "virtual_source:NXslit": {
                "x_gap": DeviceDataset("dvv"),
                "y_gap": DeviceDataset("dvh"),
            },
            "middle_focus:NXslit": {
                "x_gap": DeviceDataset("dmf"),
            },
            "diaphragm_1:NXslit": {
                "bottom:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d1b",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "top:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d1t",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "left:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d1l",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "right:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d1r",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "distance":  DeviceDataset("distances", "diaphragm1",
                                           vector=(0, 0, 1),
                                           transformation_type="translation",
                                           offset=DeviceAttribute("distances",
                                                                  "nxoffset")),
            },
            "diaphragm_2:NXslit": {
                "bottom:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d2b",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "top:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d2t",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "left:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d2l",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "right:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d2r",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "vertical_lift:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d2z",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "distance":  DeviceDataset("distances",
                                           parameter="diaphragm2",
                                           vector=(0, 0, 1),
                                           transformation_type="translation",
                                           offset=DeviceAttribute("distances",
                                                                  "nxoffset")),
            },
            "diaphragm_3:NXslit": {
                "bottom:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d3b",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "top:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d3t",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "left:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d3l",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "right:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d3r",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "vertical_lift:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d3z",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "distance": DeviceDataset("distances",
                                          parameter="diaphragm3",
                                          vector=(0, 0, 1),
                                          transformation_type="translation",
                                          offset=DeviceAttribute("distances",
                                                                 "nxoffset")),
            },
            "diaphragm_4:NXslit": {
                "vertical_gap:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d4v",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "horizontal_gap:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="d4h",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "distance": DeviceDataset("distances",
                                          parameter="diaphragm4",
                                          vector=(0, 0, 1),
                                          transformation_type="translation",
                                          offset=DeviceAttribute("distances",
                                                                 "nxoffset")),
            },
            # chopper
            "chopper:NXdisk_chopper": {
                "type": "contra_rotating_pair",
                "pair_separation": NXDataset(1000.0, dtype="float"),
                "slits": "2",
                "rotation_speed:NXevent_data": {
                    "speed": EventStream(topic=metaTopic,
                                         source="ch1_speed",
                                         mod=metaMod,
                                         dtype="double", ),
                    "units": "rpm",
                },
                "phase:NXevent_data": {
                    "phase": EventStream(topic=metaTopic,
                                         source="ch2_position",
                                         mod=metaMod,
                                         dtype="double",
                                         units="deg"),
                },
                "ratio:NXevent_data": {
                    "ratio": EventStream(topic=metaTopic,
                                         source="ch2_gear_ratio",
                                         mod=metaMod,
                                         dtype="double", ),
                },
                "distance": DeviceDataset("distances",
                                          parameter="chopper",
                                          vector=(0, 0, 1),
                                          transformation_type="translation",
                                          offset=DeviceAttribute("distances",
                                                                 "nxoffset")),
            },
            # polarizer & flipper
            "polarizer:NXploariser": {
                "type": "supermirror",
                "geometry": "transmission",
                "position_1": EventStream(topic=metaTopic,
                                          source="pz1",
                                          mod=metaMod,
                                          dtype="double", ),
                "position_2": EventStream(topic=metaTopic,
                                          source="pz2",
                                          mod=metaMod,
                                          dtype="double", ),
            },
            "spin_flipper:NXflipper": {
                "type": "RF coil",
                #    "spin_state": EventStream(topic=metaTopic,
                #                              source="???",
                #                              mod=metaMod,
                #                              dtype="int", ),
            },
            # analyser flipper !!!
            # analyser !!!
            # spin state .... !!!
            # deflector
            "deflector:NXmirror": {
                "type": "single",
                "inclination:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="lom",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "deg",
                },
                "vertical_position:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="ltz",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "mm",
                },
                "distance": DeviceDataset("distances",
                                          parameter="deflector",
                                          vector=(0, 0, 1),
                                          transformation_type="translation",
                                          offset=DeviceAttribute("distances",
                                                                 "nxoffset")),
            },
            # detector
            "detector:NXdetector": {
                "acquisition_mode": "event",
                "polar_angle:NXevent_data": {
                    "position": EventStream(topic=metaTopic,
                                            source="nu",
                                            mod=metaMod,
                                            dtype="double", ),
                    "units": "deg",
                },
                "data:NXevent_data": {
                    "data": EventStream(topic="amor_ev44",
                                        mod="ev44",
                                        source="multiblade",
                                        dtype="uint32"),
                },
                "proton_current:NXevent_data": {
                    "value": EventStream(topic=metaTopic,
                                         source="MHC6:IST:2",
                                         mod=metaMod,
                                         dtype="double", ),
                    "units": "mC",
                },
                "monitor:NXevent_data": {
                    "monitor": EventStream(topic="amor_beam_monitor",
                                           mod="ev44",
                                           source="ttlmon0",
                                           dtype="uint32"),
                },
                "depends_on": "transformation/distance",
                "transformation:NXtransformations": {
                    "height:NXevent_data": {
                        "vector": (0, 0, 1),
                        "attributes": "",
                        "depends_on": "rotation",
                        "transformation_type": "translation",
                        "value": EventStream(topic=metaTopic,
                                             source="coz",
                                             mod=metaMod,
                                             dtype="double", ),
                        "units": "mm",
                    },
                    "rotation:NXevent_data": {
                        "vector": (0, 1, 0),
                        "attributes": "",
                        "depends_on": ".",
                        "transformation_type": "rotation",
                        "value": EventStream(topic=metaTopic,
                                             source="com",
                                             mod=metaMod,
                                             dtype="double", ),
                        "units": "deg",
                    },
                    "distance":
                        DeviceDataset("distances",
                                      parameter="detector",
                                      vector=(0, 0, 1),
                                      transformation_type="translation",
                                      offset=DeviceAttribute("distances",
                                                             "nxoffset")),
                },
            },
            # monitor !!!
            # sample stage
            "sample_stage:NXsample": {
                "sch": DeviceDataset("sch"),
                "mud": DeviceDataset("mud"),
                "base_height": DeviceDataset("szoffset"),
                "depends_on": "transformation/height",
                "transformation:NXtransformations": {
                    "height:NXevent_data": {
                        "offset": "",  # stz
                        "vector": (0, 1, 0),
                        "attributes": "",
                        "depends_on": "rotation",
                        "transformation_type": "translation",
                        "value": EventStream(topic=metaTopic,
                                             source="soz",
                                             mod=metaMod,
                                             dtype="double", ),
                        "units": "mm",
                    },
                    "rotation:NXevent_data": {
                        "vector": (1, 0, 0),
                        "attributes": "",
                        "depends_on": ".",
                        "transformation_type": "rotation",
                        "value": EventStream(topic=metaTopic,
                                             source="som",
                                             mod=metaMod,
                                             dtype="double", ),
                        "units": "deg",
                    },
                },
                "distance": DeviceDataset("distances", "sample",
                                          vector=(0, 0, 1),
                                          transformation_type="translation",
                                          offset=DeviceAttribute("distances",
                                                                 "nxoffset")),
            },
        },  # end of instrument
        # sample description and environment
        "sample:NXsample": {
            # declaration
            "name": DeviceDataset("Sample", "samplename"),
            "model": DeviceDataset("Sample", "orsomodel"),
            # beam geometry
            "kappa:NXevent_data": {
                "position": EventStream(topic=metaTopic,
                                        source="kap",
                                        mod=metaMod,
                                        dtype="double", ),
                "units": "deg",
            },
            "mu:NXevent_data": {
                "position": EventStream(topic=metaTopic,
                                        source="mu",
                                        mod=metaMod,
                                        dtype="double", ),
                "units": "deg",
            },
            "div:NXevent_data": {
                "position": EventStream(topic=metaTopic,
                                        source="div",
                                        mod=metaMod,
                                        dtype="double", ),
                "units": "deg",
            },
            "kad": DeviceDataset("kad"),
            # alignment parameters !!! redundand, see sample_stage
            "sch": DeviceDataset("sch"),
            "mud": DeviceDataset("mud"),
            "base_height": DeviceDataset("szoffset"),
            "depends_on": "transformation/height",
            "transformation:NXtransformations": {
                "height:NXevent_data": {
                    "offset": "",  # stz
                    "vector": (0, 1, 0),
                    "attributes": "",
                    "depends_on": "rotation",
                    "transformation_type": "translation",
                    "value": EventStream(topic=metaTopic,
                                         source="soz",
                                         mod=metaMod,
                                         dtype="double", ),
                    "units": "mm",
                },
                "height_offset:NXevent_data": {
                    "offset": "",  # stz
                    "vector": (0, 1, 0),
                    "attributes": "",
                    "depends_on": "rotation",
                    "transformation_type": "translation",
                    "value": EventStream(topic=metaTopic,
                                         source="stz",
                                         mod=metaMod,
                                         dtype="double", ),
                    "units": "mm",
                },
                "rotation:NXevent_data": {
                    "vector": (1, 0, 0),
                    "attributes": "",
                    "depends_on": ".",
                    "transformation_type": "rotation",
                    "value": EventStream(topic=metaTopic,
                                         source="som",
                                         mod=metaMod,
                                         dtype="double", ),
                    "units": "deg",
                },
            },
            "temperature:NXevent_data": {
                    "value": EventStream(topic=metaTopic,
                                         source="temperature",
                                         mod=metaMod,
                                         dtype="double", ),
                    "units": "K",
            },
            "magnetic_field:NXevent_data": {
                    "value": EventStream(topic=metaTopic,
                                         source="magnetic_field",
                                         mod=metaMod,
                                         dtype="double", ),
                    "units": "A",
            },
            # geometry
            "distance": DeviceDataset("distances", "sample",
                                      vector=(0, 0, 1),
                                      transformation_type="translation",
                                      offset=DeviceAttribute("distances",
                                                             "nxoffset")),
        },  # end of sample
    },  # end of entry1
}
