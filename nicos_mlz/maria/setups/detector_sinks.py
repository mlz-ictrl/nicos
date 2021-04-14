# -*- coding: utf-8 -*-

description = "Datasinks used for writing and viewing detector data"
group = "lowlevel"

sysconfig = dict(
    datasinks = ["NPGZFileSink", "YAMLSaver", "LiveViewSink"],
)

basename = "%(proposal)s_%(session.experiment.sample.filename)s_"
scanbasename = basename + "%(scancounter)08d_%(pointnumber)08d"
countbasename = basename + "%(pointpropcounter)010d"

devices = dict(
    NPGZFileSink = device("nicos.devices.datasinks.text.NPGZFileSink",
        description = "Saves image data in numpy text "
        "format",
        filenametemplate = [
            scanbasename + "_%(arraynumber)d.gz",
            countbasename + "_%(arraynumber)d.gz",
        ],
    ),
    YAMLSaver = device("nicos_mlz.maria.devices.yamlformat.YAMLFileSink",
        filenametemplate = [
            scanbasename + ".yaml",
            countbasename + ".yaml",
        ],
    ),
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
)
