# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"


description = "Axes setup"
group = "optional"

_TANGO_SRV = "phys.biodiff.frm2:10000"
_TANGO_URL = "tango://" + _TANGO_SRV + "/biodiff/FZJS7/"

devices = dict(
        omega_samplestepper = device("devices.tango.Motor",
                                     description = "Sample stepper " +
                                     "omega variant",
                                     tangodevice = _TANGO_URL +
                                     "omega_samplestepper",
                                     unit = "deg",
                                     ),
        omega_sampletable = device("devices.tango.Motor",
                                   description = "Sample table omega variant",
                                   tangodevice = _TANGO_URL +
                                   "omega_sampletable",
                                   unit = "deg",
                                   ),
        x_sampletable = device("devices.tango.Motor",
                               description = "Sample table x axis",
                               tangodevice = _TANGO_URL + "x_sampletable",
                               unit = "mm",
                               ),
        y_sampletable = device("devices.tango.Motor",
                               description = "Sample table y axis",
                               tangodevice = _TANGO_URL + "y_sampletable",
                               unit = "mm",
                               ),
        z_sampletable = device("devices.tango.Motor",
                               description = "Sample table x axis",
                               tangodevice = _TANGO_URL + "z_sampletable",
                               unit = "mm",
                               ),
        theta_monochromator = device("devices.tango.Motor",
                                     description = "Monochromator theta " +
                                     "variant",
                                     tangodevice = _TANGO_URL +
                                     "theta_monochromator",
                                     unit = "deg",
                                     ),
        tilt_monochromator = device("devices.tango.Motor",
                                    description = "Monochromator tilt",
                                    tangodevice = _TANGO_URL +
                                    "tilt_monochromator",
                                    unit = "deg",
                                    ),
        x_monochromator = device("devices.tango.Motor",
                                 description = "Monochromator x axis",
                                 tangodevice = _TANGO_URL + "x_monochromator",
                                 unit = "mm",
                                 ),
        y_monochromator = device("devices.tango.Motor",
                                 description = "Monochromator y axis",
                                 tangodevice = _TANGO_URL + "y_monochromator",
                                 unit = "mm",
                                 ),
        z_monochromator = device("devices.tango.Motor",
                                 description = "Monochromator z axis",
                                 tangodevice = _TANGO_URL + "z_monochromator",
                                 unit = "mm",
                                 ),
        theta2_selectorarm = device("devices.tango.Motor",
                                    description = "Selector arm 2theta variant",
                                    tangodevice = _TANGO_URL +
                                    "2theta_selectorarm",
                                    unit = "deg",
                                    ),
        d_diaphragm1 = device("devices.tango.Motor",
                              description = "Slit 1",
                              tangodevice = _TANGO_URL + "d_diaphragm1",
                              unit = "mm",
                              ),
        d_diaphragm2 = device("devices.tango.Motor",
                              description = "Slit 2",
                              tangodevice = _TANGO_URL + "d_diaphragm2",
                              unit = "mm",
                              ),
        theta2_detectorunit = device("devices.tango.Motor",
                                     description = "Detector unit " +
                                     "2theta variant",
                                     tangodevice = _TANGO_URL +
                                     "2theta_detectorunit",
                                     unit = "deg",
                                     ),
        z_imageplate = device("devices.tango.Motor",
                              description = "Neutron image plate z axis",
                              tangodevice = _TANGO_URL +
                              "z_neutronimageplate",
                              unit = "mm",
                              ),
        z_CCD = device("devices.tango.Motor",
                       description = "CCD z axis",
                       tangodevice = _TANGO_URL + "z_CCD",
                       unit = "mm",
                       ),
        z_CCDcamera = device("devices.tango.Motor",
                             description = "CCD camera z axis",
                             tangodevice = _TANGO_URL + "z_CCDcamera",
                             unit = "mm",
                             ),
        theta2_CCDcamera = device("devices.tango.Motor",
                                  description = "CCD camera 2theta variant",
                                  tangodevice = _TANGO_URL + "2theta_CCDcamera",
                                  unit = "deg",
                                  ),
        rot_scintillatorhead = device("devices.tango.Motor",
                                      description = "Scintillator head " +
                                      "rotation",
                                      tangodevice = _TANGO_URL +
                                      "rot_scintillatorhead",
                                      unit = "deg",
                                      ),
#        omega_samplegoniometer = device("devices.tango.Motor",
#                                    description = "Sample goniometer " +
#                                    "omega variant",
#                                    tangodevice = _TANGO_URL +
#                                    "omega_samplegoniometer",
#                                    ),
#        x_samplegoniometer = device("devices.tango.Motor",
#                                    description = "Sample goniometer x axis",
#                                    tangodevice = _TANGO_URL +
#                                    "x_samplegoniometer",
#                                    ),
#        y_samplegoniometer = device("devices.tango.Motor",
#                                    description = "Sample goniometer y axis",
#                                    tangodevice = _TANGO_URL +
#                                    "y_samplegoniometer",
#                                    ),
#        rot_diaphragm3 = device("devices.tango.Motor",
#                                description = "Slit 3",
#                                 tangodevice = _TANGO_URL + "rot_diaphragm3",
#                                 unit = "deg",
#                                 ),
#         rot_diaphragm4 = device("devices.tango.Motor",
#                                 description = "Slit 4",
#                                 tangodevice = _TANGO_URL + "rot_diaphragm4",
#                                 unit = "deg",
#                                 ),
               )
