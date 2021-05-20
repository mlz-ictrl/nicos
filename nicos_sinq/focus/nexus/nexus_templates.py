#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************
from copy import deepcopy

from nicos import session
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, NamedImageDataset, NexusSampleEnv, \
    NXAttribute, NXLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_sinq.focus.nexus.focus import FocusCoordinates, ScaledImage, \
    SliceTofImage, SumImage
from nicos_sinq.nexus.specialelements import ConfArray, FixedArray, \
    TwoThetaArray

focus_default = {"NeXus_Version": "4.4.0",
                 "instrument": "FOCUS at SINQ",
                 "owner": DeviceAttribute("FOCUS", "responsible"),
                 "entry1:NXentry": {
                    "title": DeviceDataset("Exp", "title"),
                    "proposal_title": DeviceDataset("Exp", "title"),
                    "proposal_id": DeviceDataset("Exp", "proposal"),
                    "start_time": NXTime(),
                    "end_time": NXTime(),
                    "definition": ConstDataset("NXdirecttof", "string"),
                    "duration": DetectorDataset("elapsedtime",
                                                dtype="float32"),
                    "pre_sample_flightpath":
                    NXLink("/entry1/FOCUS/fermi_chopper/distance"),
                    "user:NXuser": {
                        "name": DeviceDataset("Exp", "users"),
                        "email": DeviceDataset("Exp", "localcontact")
                    },
                    "sample:NXsample": {
                        "name": DeviceDataset("Sample", "samplename"),
                        "temperature": DeviceDataset("temperature", "value",
                                                     defaultval=0.0),
                        "hugo": NexusSampleEnv(),
                        "distance": ConstDataset(499.7, "float32",
                                                 units=NXAttribute("mm",
                                                                   "string")),
                        "angle": ConstDataset(0., "float32",
                                              units=NXAttribute("degree",
                                                                "string")),
                    },
                    "FOCUS:NXinstrument": {
                        "name": ConstDataset("FOCUS", "string"),
                        "SINQ:NXsource": {
                            "name": ConstDataset(
                                "SINQ, Paul Scherrer Institute", "string"),
                            "type": ConstDataset(
                                "continuous flux spallation source", "string"),
                            "probe": ConstDataset("neutron", "string"),
                        },
                     },  # instrument
                    }  # entry
                 }

focus_counter = {
    "preset": DetectorDataset("preset", "float32"),
    "count_mode": DetectorDataset("mode", "string"),
    "monitor": DetectorDataset("monitor1", "int32",
                               units=NXAttribute("counts", "string")),
    "monitor_check": DetectorDataset("tof_sum", "int32",
                                     units=NXAttribute("counts", "string")),
    "time": DetectorDataset("elapsedtime", "float32",
                            units=NXAttribute("seconds", "string")),
    "proton_beam_monitor": DetectorDataset("protoncount", "int32",
                                           units=NXAttribute("counts",
                                                             "string")),
    "monitor_distance": ConstDataset(2784., "float32",
                                     units=NXAttribute("mm", "string")),
    "beam_monitor": DetectorDataset("beam_monitor", "int32",
                                    units=NXAttribute("counts", "string")),

}

tof_monitor = {
    "preset": DetectorDataset("preset", "float32"),
    "mode": NXLink("/entry1/FOCUS/counter/count_mode"),
    "integral_counts": DetectorDataset("tof_sum", "int32",
                                       units=NXAttribute("counts", "string")),
    "distance": ConstDataset(2784., "float32",
                             units=NXAttribute("mm", "string")),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),

}
disk_chopper = {
    "name": ConstDataset("Dornier disk chopper", "string"),
    "rotation_speed": DeviceDataset("ch2_speed"),
    "ratio": DeviceDataset("ch_ratio"),
    "energy": DeviceDataset("ei"), }

fermi_chopper = {
    "name": ConstDataset("Dornier Fermi chopper", "string"),
    "rotation_speed": DeviceDataset("ch1_speed"),
    "phase": DeviceDataset("ch_phase"),
    "distance": DeviceDataset("fermidist", "float32",
                              units=NXAttribute("mm", "string")),
    "energy": DeviceDataset("ei"),
}

flight_path = {
    "selection": ConstDataset("Standard", "string"),
    "length": DeviceDataset("fermidist", "float32",
                            units=NXAttribute("mm", "string")),
}

monochromator = {
    "lambda": DeviceDataset("wavelength"),
    "d_spacing": DeviceDataset("wavelength", "dvalue"),
    "theta": DeviceDataset("mth"),
    "two_theta": DeviceDataset("mtt"),
    "monochromator1_horizontal_curvature": DeviceDataset("m1ch"),
    "monochromator1_vertical_curvature": DeviceDataset("m1cv"),
    "monochromator2_horizontal_curvature": DeviceDataset("m2ch"),
    "monochromator2_vertical_curvature": DeviceDataset("m2cv"),
    "x_translation": DeviceDataset("mtx"),
    "y_translation": DeviceDataset("mty"),
    "monochromator_lift": DeviceDataset("mex"),
    "monochromator_rotation": DeviceDataset("mgo"),
    "msl": DeviceDataset("msl"),
    "name": ConstDataset("Graphite Monochromator", "string"),
}

det_common = {
    "delay": DeviceDataset("delay"),
    "time_binning": ConfArray("hm_tof_array",
                              units=NXAttribute("us", "string"),
                              axis=NXAttribute(2, "int32"),
                              scale=.1,
                              ),
}

middlebank = {
    "counts": NamedImageDataset('middle_image',
                                signal=NXAttribute(1, 'int32')),
    "theta": ConfArray("middle_theta",
                       units=NXAttribute("degree", "string"),
                       axis=NXAttribute(1, "int32")),
    "data": NXLink("/entry1/FOCUS/bank1/counts"),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "polar_angle": NXLink("/entry1/FOCUS/bank1/theta"),
    "azimuthal_angle": ConstDataset(.0, dtype="float32",
                                    units=NXAttribute("degree", "string")),
    "detector_number": FixedArray(0, 1, 150, dtype='int32'),
    "distance": TwoThetaArray("sampledist", 0, 150, dytpe="float32",
                              units=NXAttribute("mm", "string")),
    "summed_counts": SumImage('middle_image', 150, dtype='int32')
}

middle_data = {
    "counts": NXLink("/entry1/FOCUS/bank1/counts"),
    "time_binning": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "data": NXLink("/entry1/FOCUS/bank1/counts"),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "theta": NXLink("/entry1/FOCUS/bank1/theta"),
    "detector_number": NXLink("/entry1/FOCUS/bank1/detector_number"),
}

upperbank = {
    "counts": NamedImageDataset('upper_image',
                                signal=NXAttribute(1, 'int32')),
    "theta": ConfArray("upper_theta",
                       units=NXAttribute("degree", "string"),
                       axis=NXAttribute(1, "int32")),
    "time_binning": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "delay": NXLink("/entry1/FOCUS/bank1/delay"),
    "data": NXLink("/entry1/FOCUS/upperbank/counts"),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "polar_angle": NXLink("/entry1/FOCUS/upperbank/theta"),
    "detector_number": FixedArray(0, 1, 110, dtype='int32'),
    "distance": FixedArray(2000, 0, 110, dtype="float32",
                           units=NXAttribute("mm", "string")),
    "azimuthal_angle": ConstDataset(13., dtype="float32",
                                    units=NXAttribute("degree", "string")),
    "summed_counts": SumImage('upper_image', 110, dtype='int32'),
}

upper_data = {
    "counts": NXLink("/entry1/FOCUS/upperbank/counts"),
    "time_binning": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "theta": NXLink("/entry1/FOCUS/upperbank/theta"),
    "data": NXLink("/entry1/FOCUS/upperbank/counts"),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "detector_number": NXLink("/entry1/FOCUS/upperbank/detector_number"),
}

lowerbank = {
    "counts": SliceTofImage('lower_image', 'hm_tof_array',
                            0, 115,
                            signal=NXAttribute(1, 'int32')),
    "theta": ConfArray("lower_theta",
                       units=NXAttribute("degree", "string"),
                       axis=NXAttribute(1, "int32")),
    "time_binning": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "delay": NXLink("/entry1/FOCUS/bank1/delay"),
    "data": NXLink("/entry1/FOCUS/lowerbank/counts"),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "polar_angle": NXLink("/entry1/FOCUS/lowerbank/theta"),
    "detector_number": FixedArray(0, 1, 115, dtype='int32'),
    "distance": FixedArray(2000, 0, 115, dtype="float32",
                           units=NXAttribute("mm", "string")),
    "azimuthal_angle": ConstDataset(-13., dtype="float32",
                                    units=NXAttribute("degree", "string")),
    "summed_counts": SumImage('lower_image', 116, dtype='int32'),
}


lower_data = {
    "counts": NXLink("/entry1/FOCUS/lowerbank/counts"),
    "time_binning": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "theta": NXLink("/entry1/FOCUS/lowerbank/theta"),
    "data": NXLink("/entry1/FOCUS/lowerbank/counts"),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "detector_number": NXLink("/entry1/FOCUS/lowerbank/detector_number"),
}

mergedbank = {
    "counts": NamedImageDataset('merged_image',
                                signal=NXAttribute(1, 'int32')),
    "theta": ConfArray("merged_theta",
                       units=NXAttribute("degree", "string"),
                       axis=NXAttribute(1, "int32")),
    "time_binning": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "delay": NXLink("/entry1/FOCUS/bank1/delay"),
    "data": NXLink("/entry1/FOCUS/merged/counts"),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "polar_angle": NXLink("/entry1/FOCUS/merged/theta"),
    "azimuthal_angle": ConstDataset(.0, dtype="float32",
                                    units=NXAttribute("degree", "string")),
    "detector_number": FixedArray(0, 1, 375, dtype='int32'),
    "distance": FixedArray(2000, 0, 375, dtype="float32",
                           units=NXAttribute("mm", "string")),
    "summed_counts": SumImage('merged_image', 375, dtype='int32')
}

merged_data = {
    "counts": NXLink("/entry1/FOCUS/merged/counts"),
    "time_binning": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "theta": NXLink("/entry1/FOCUS/merged/theta"),
    "data": NXLink("/entry1/FOCUS/merged/counts"),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "detector_number": NXLink("/entry1/FOCUS/merged/detector_number"),
}

f2d_bank = {
    "coord_dummy": FocusCoordinates(),
    "counts": ScaledImage('f2d_image',
                          signal=NXAttribute(1, 'int32')),
    "data": NXLink("/entry1/FOCUS/focus2d/counts"),
    "time_binning": NXLink("/entry1/FOCUS/bank1/time_binning"),
}

f2d_data = {
    "counts": NXLink("/entry1/FOCUS/focus2d/counts"),
    "data": NXLink("/entry1/FOCUS/focus2d/counts"),
    "time_binning": NXLink("/entry1/FOCUS/bank1/time_binning"),
    "time_of_flight": NXLink("/entry1/FOCUS/bank1/time_binning"),
}


class FOCUSTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        full = deepcopy(focus_default)
        entry = full["entry1:NXentry"]
        focus = entry["FOCUS:NXinstrument"]
        exp = session.getDevice("Exp")
        numor = exp.sicscounter - 1
        entry["run_number"] = ConstDataset(numor, "int32")
        focus["counter:NXmonitor"] = deepcopy(focus_counter)
        entry["monitor:NXmonitor"] = deepcopy(tof_monitor)
        focus["disk_chopper:NXchopper"] = deepcopy(disk_chopper)
        focus["fermi_chopper:NXchopper"] = deepcopy(fermi_chopper)
        focus["flight_path:NXfilter"] = deepcopy(flight_path)
        focus["monochromator:NXmonochromator"] = deepcopy(monochromator)
        bankcount = 0
        if "middlebank" in session.loaded_setups:
            middledict = {**middlebank, **det_common}
            focus["bank1:NXdetector"] = deepcopy(middledict)
            entry["bank1:NXdata"] = deepcopy(middle_data)
            bankcount += 1
        else:
            # Even if the middlebank is MIA, this contains the TOF link
            # targets
            focus["bank1:NXdetector"] = deepcopy(det_common)
        if "upperbank" in session.loaded_setups:
            focus["upperbank:NXdetector"] = deepcopy(upperbank)
            entry["upperbank:NXdata"] = deepcopy(upper_data)
            bankcount += 1
        if "lowerbank" in session.loaded_setups:
            focus["lowerbank:NXdetector"] = deepcopy(lowerbank)
            entry["lowerbank:NXdata"] = deepcopy(lower_data)
            focus["tof_monitor"] = SliceTofImage('lower_image',
                                                 'hm_tof_array',
                                                 115, 116,
                                                 signal=NXAttribute(1,
                                                                    'int32'),
                                                 units=NXAttribute("counts",
                                                                   "string"))
            entry["monitor:NXmonitor"]["data"] = \
                NXLink("/entry1/FOCUS/tof_monitor")
            bankcount += 1
        if bankcount == 3:  # Enough banks: store merged data
            focus["merged:NXdetector"] = deepcopy(mergedbank)
            entry["merged:NXdata"] = deepcopy(merged_data)
        if "focus2d" in session.loaded_setups:
            focus["focus2d:NXdetector"] = deepcopy(f2d_bank)
            entry["focus2d:NXdata"] = deepcopy(f2d_data)
        return full
