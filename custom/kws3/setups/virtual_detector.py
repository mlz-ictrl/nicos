# -*- coding: utf-8 -*-

description = "Virtual detector motor setup"
group = "lowlevel"

devices = dict(

    det_x          = device("kws1.virtual.Standin",
                            description = "detector translation X",
                           ),
    det_y          = device("kws1.virtual.Standin",
                            description = "detector translation Y",
                           ),
    det_z          = device("kws1.virtual.Standin",
                            description = "detector translation Z",
                           ),
    det_beamstop_x = device("kws1.virtual.Standin",
                            description = "detector beamstop_x",
                           ),
)
