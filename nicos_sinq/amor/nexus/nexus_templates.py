# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#   Jochen Stahn <jochen.stahn@psi.ch>
#
# *****************************************************************************

from nicos_sinq.nexus import DeviceAttribute, DeviceDataset, EventStream, \
    NXDataset, NXLink
from nicos_sinq.amor.nexus.placeholder import UserEmailPlaceholder

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
        #"start_time_epoch": DeviceDataset("dataset", "starttimeepoch"),
        #"end_time_epoch": DeviceDataset("dataset", "endtimeepoch"),
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
            #"amor_mode": DeviceDataset("amormode"),
            # instrument control parameters
            "instrument_control_parameters:NXcollection": {
                "description:NXcollection": {
                    "mu": NXDataset("Angle between instrument horizon and"
                                    " sample surface"),
                    "nu": NXDataset("Angle between instrument horizon and"
                                    " sample-detector"),
                    "kappa": NXDataset("Angle between instrument horizon"
                                       " and beam center at the sample."
                                       " Depends on the deflector angle 'lom'"
                                       " and the first diaphragm vertical "
                                       " opening."),
                    "div": NXDataset("Vertical divergence of the beam incident"
                                     " on the sample. Defined by the first"
                                     " diaphragm vertical opening."),
                    "kappa_offset": NXDataset("Offset of the actual beam center with "
                                              " respect to full beam center. Defined"
                                              " by the first diaphragm vertical opening"
                                              " and probably by the deflector position"
                                              " 'ltz' and angle 'lom'."),
                    },
                "mu": DeviceDataset("mu"),
                "nu": DeviceDataset("nu"),
                "kappa": DeviceDataset("kappa"),
                "kappa_offset": DeviceDataset("kad"),
                "div": DeviceDataset("div"),
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
                "top": DeviceDataset("d1t"),
                "left": DeviceDataset("d1l"),
                "right": DeviceDataset("d1r"),
                "bottom": DeviceDataset("d1b"),
                "distance": DeviceDataset("distances", "diaphragm1",
                                          vector=(0, 0, 1),
                                          transformation_type="translation",
                                          offset=DeviceAttribute("distances",
                                                                 "nxoffset")),
                },
            "diaphragm_2:NXslit": {
                "top": DeviceDataset("d2t"),
                "left": DeviceDataset("d2l"),
                "right": DeviceDataset("d2r"),
                "bottom": DeviceDataset("d2b"),
                "vertical_lift": DeviceDataset("d2z"),
                "distance": DeviceDataset("distances",
                                          parameter="diaphragm2",
                                          vector=(0, 0, 1),
                                          transformation_type="translation",
                                          offset=DeviceAttribute("distances",
                                                                 "nxoffset")),
                },
            "diaphragm_3:NXslit": {
                "top": DeviceDataset("d3t"),
                "left": DeviceDataset("d3l"),
                "right": DeviceDataset("d3r"),
                "bottom": DeviceDataset("d3b"),
                "vertical_lift": DeviceDataset("d3z"),
                "distance": DeviceDataset("distances",
                                          parameter="diaphragm3",
                                          vector=(0, 0, 1),
                                          transformation_type="translation",
                                          offset=DeviceAttribute("distances",
                                                                 "nxoffset")),
                },
            "diaphragm_4:NXslit": {
                "vertical_gap": DeviceDataset("d4v"),
                "horizontal_gap": DeviceDataset("d4h"),
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
                "pair_separation": NXDataset(1000.0, dtype="float", uint="mm"),
                "slits": NXDataset(2, dtype="int"),
                #"rotation_speed:NXlog": {
                #    "speed": EventStream(topic=metaTopic,
                #                         source="ch1_speed",
                #                         mod=metaMod,
                #                         dtype="double"),
                #    "units": "rpm",
                #    },
                "distance": DeviceDataset("distances",
                                          parameter="chopper",
                                          vector=(0, 0, 1),
                                          transformation_type="translation",
                                          offset=DeviceAttribute("distances",
                                                                 "nxoffset")),
                "rotation_speed": DeviceDataset("ch1_speed"),
                "ratio": DeviceDataset("ch2_gear_ratio"),
                "phase": DeviceDataset("chopper_phase"),
                "trigger_phase": DeviceDataset("ch2_phase"),
                "ch1_trigger_phase": DeviceDataset("ch1_trigger_phase"),
                "ch2_trigger_phase": DeviceDataset("ch2_trigger_phase"),
                "ch2_trigger:NXevent_data": {
                    "ch2_trigger": EventStream(topic="amor_beam_monitor",
                                               mod="ev44",
                                               source="ttlmon0",
                                               dtype="uint32",
                                               chunk_size=16384),
                    },
                },
            # polarizer & flipper
            "polarization:NXcollection": {
                "polarizer_stage:NXploariser": {
                    "type": "supermirror",
                    "geometry": "transmission",
                    "z-position_1": DeviceDataset("pz1"),
                    "z-position_2": DeviceDataset("pz2"),
                    },
                "spin_flipper:NXflipper": {
                    "type": "RF coil",
                    "flip_current": EventStream(topic=metaTopic,
                                                source="spinflipper_amp",
                                                mod=metaMod,
                                                dtype="double"),
                    #"frequency": DeviceDataset("spinflipper_amp"),
                    },
                "configuration:NXlog": {
                    "value": EventStream(topic=metaTopic,
                                         source="polarization_config",
                                         mod=metaMod,
                                         dtype="int"),
                    },
                },
            # deflector
            "deflector:NXmirror": {
                "type": "single",
                "inclination:NXlog": {
                    "position": EventStream(topic=metaTopic,
                                            source="lom",
                                            mod=metaMod,
                                            dtype="double"),
                    "units": "deg",
                    },
                "vertical_position:NXlog": {
                    "position": EventStream(topic=metaTopic,
                                            source="ltz",
                                            mod=metaMod,
                                            dtype="double"),
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
                "polar_angle": DeviceDataset("nu"),
                "data:NXevent_data": {
                    "data": EventStream(topic="amor_ev44",
                                        mod="ev44",
                                        source="multiblade",
                                        dtype="uint32",
                                        chunk_size=16384),
                    },
                #"proton_monitor:NXlog": {
                #    "value": EventStream(topic=metaTopic,
                #                         source="proton_monitor",
                #                         mod=metaMod,
                #                         dtype="double"),
                #    "units": "mC",
                #    },
                # closer to real time, needs EPICS_forwarder, uses old protocol
                #"proton_current:NXlog": {
                #    "value": EventStream(topic='AMOR_epics',
                #                         source="SQ:AMOR:sumi:BEAMCPY",
                #                         mod="f142",
                #                         dtype="double"),
                #    "units": "uA",
                #    },
                # signal via nicos: 0.2 ms behind direct feed from EPICS
                "proton_current:NXlog": {
                    "value": EventStream(topic=metaTopic,
                                         source="proton_current",
                                         mod=metaMod,
                                         dtype="double",
                                         chunk_size=16384),
                    "units": "uA",
                    },
                #"ch2_trigger:NXlog": {
                #    "data": EventStream(topic="amor_ch2_trigger",
                #                        mod="ev44",
                #                        source="ttlmon0",
                #                        dtype="uint32"),
                #    },
                "monitor:NXevent_data": {
                    "monitor": EventStream(topic="amor_beam_monitor",
                                           mod="ev44",
                                           source="ttlmon0",
                                           dtype="uint32",
                                           chunk_size=16384),
                    },
                "depends_on": "transformation/distance",
                "transformation:NXtransformations": {
                    "height": DeviceDataset("det_zoffset"),
                    "rotation": DeviceDataset("det_nu"),
                    "distance": DeviceDataset("distances",
                                              parameter="detector",
                                              vector=(0, 0, 1),
                                              transformation_type="translation",
                                              offset=DeviceAttribute("distances",
                                                                     "nxoffset")),
                    },
                },
            # sample stage
            "sample_stage:NXsample": {
                "sample_alignment_roll": DeviceDataset("sample_roll"),
                "sample_alignment_tilt": DeviceDataset("sample_tilt"),
                "sample_alignment_height": DeviceDataset("sample_height"),
                "depends_on": "transformation/height",
                "transformation:NXtransformations": {
                    "height:NXlog": {
                        "offset": "",  # stz
                        "vector": (0, 1, 0),
                        "attributes": "",
                        "depends_on": "rotation",
                        "transformation_type": "translation",
                        "value": EventStream(topic=metaTopic,
                                             source="soz",
                                             mod=metaMod,
                                             dtype="double"),
                        "units": "mm",
                        },
                    "rotation:NXlog": {
                        "vector": (1, 0, 0),
                        "attributes": "",
                        "depends_on": ".",
                        "transformation_type": "rotation",
                        "value": EventStream(topic=metaTopic,
                                             source="som",
                                             mod=metaMod,
                                             dtype="double"),
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
            "stack": DeviceDataset("Sample", "orsomodel"),
            "model": DeviceDataset("Sample", "yaml"),
            # beam geometry
            "kappa": DeviceDataset("kappa"),
            "mu": DeviceDataset("mu"),
            "divergence": DeviceDataset("div"),
            "delta_kappa": DeviceDataset("kad"),
            "alpha_i": DeviceDataset("alpha_i"),
            "alpha_f": DeviceDataset("alpha_f"),
            "depends_on": "transformation/height",
            "transformation:NXtransformations": {
                "height:NXlog": {
                    "offset": "",  # stz
                    "vector": (0, 1, 0),
                    "attributes": "",
                    "depends_on": "rotation",
                    "transformation_type": "translation",
                    "value": EventStream(topic=metaTopic,
                                         source="soz",
                                         mod=metaMod,
                                         dtype="double"),
                    "units": "mm",
                    },
                "height_offset:NXlog": {
                    "offset": "",  # stz
                    "vector": (0, 1, 0),
                    "attributes": "",
                    "depends_on": "rotation",
                    "transformation_type": "translation",
                    "value": EventStream(topic=metaTopic,
                                         source="stz",
                                         mod=metaMod,
                                         dtype="double"),
                    "units": "mm",
                    },
                "rotation:NXlog": {
                    "vector": (1, 0, 0),
                    "attributes": "",
                    "depends_on": ".",
                    "transformation_type": "rotation",
                    "value": EventStream(topic=metaTopic,
                                         source="som",
                                         mod=metaMod,
                                         dtype="double"),
                    "units": "deg",
                    },
                },
            "temperature:NXlog": {
                "value": EventStream(topic=metaTopic,
                                     # source="temperature",
                                     source="se_tt",
                                     mod=metaMod,
                                     dtype="double"),
                "units": "K",
                },
            "magnetic_field:NXlog": {
                "value": EventStream(topic=metaTopic,
                                     source="fma",
                                     mod=metaMod,
                                     dtype="double"),
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
