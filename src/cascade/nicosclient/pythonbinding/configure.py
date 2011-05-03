#!/usr/bin/python

import os
import sipconfig
from PyQt4 import pyqtconfig

build_file = "cascadeclient.sbf"

config = pyqtconfig.Configuration()
pyqt_sip_flags = config.pyqt_sip_flags

print "Running sip..."
os.system(" ".join([config.sip_bin, "-c", ".", "-b", build_file, "-I", config.pyqt_sip_dir, pyqt_sip_flags, "cascadeclient.sip"]))

print "Generating makefile..."
makefile = pyqtconfig.QtGuiModuleMakefile(configuration=config, build_file=build_file)

makefile.extra_libs = ["cascadeclient", "QtNetwork"]
makefile.extra_lib_dirs = [".."]
makefile.generate()
