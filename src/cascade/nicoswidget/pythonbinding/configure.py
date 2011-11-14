#!/usr/bin/python

import os
import sipconfig
from PyQt4 import pyqtconfig

build_file = "cascadewidget.sbf"

config = pyqtconfig.Configuration()
pyqt_sip_flags = config.pyqt_sip_flags

print "Running sip..."
os.system(" ".join([config.sip_bin, "-t", "Qwt_5_2_0", "-c", ".", "-b", build_file, "-I", config.pyqt_sip_dir, pyqt_sip_flags, "cascadewidget.sip"]))

print "Generating makefile..."
makefile = pyqtconfig.QtGuiModuleMakefile(configuration=config, build_file=build_file)

makefile.extra_include_dirs = ["/usr/include/qwt", "/usr/include/qwt5", ".."]
makefile.extra_libs = ["cascadewidget", "Minuit2", "gomp", "QtNetwork", "qwt"]
makefile.extra_lib_dirs = [".."]
makefile.generate()
