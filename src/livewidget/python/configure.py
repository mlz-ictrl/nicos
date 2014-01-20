#!/usr/bin/python

from __future__ import print_function

import os, re, sys, glob, platform
from os.path import basename
from PyQt4 import pyqtconfig

def fix_build_file(name, extra_sources, extra_headers, extra_moc_headers):
    # from PyQwt
    keys = ('target', 'sources', 'headers', 'moc_headers')
    sbf = {}
    for key in keys:
        sbf[key] = []

    # Parse,
    nr = 0
    for line in open(name, 'r'):
        nr += 1
        if line[0] != '#':
            eq = line.find('=')
            if eq == -1:
                raise RuntimeError(
                    '"%s\" line %d: Line must be in the form '
                    '"key = value value...."' % (name, nr))
        key = line[:eq].strip()
        value = line[eq+1:].strip()
        if key in keys:
            sbf[key].append(value)

    # extend,
    sbf['sources'].extend(extra_sources)
    sbf['headers'].extend(extra_headers)
    sbf['moc_headers'].extend(extra_moc_headers)

    # and write.
    output = open(name, 'w')
    for key in keys:
        if sbf[key]:
            print('%s = %s' % (key, ' '.join(sbf[key])), file=output)


build_file = "livewidget.sbf"

config = pyqtconfig.Configuration()
pyqt_sip_flags = config.pyqt_sip_flags

print("Running sip...")
os.system(" ".join([config.sip_bin, "-t", "Qwt_5_2_0", "-c", ".", "-b", build_file,
                    "-I", config.pyqt_sip_dir, pyqt_sip_flags, "livewidget.sip"]))

# set up including the livewidget sources directly in the build
print("Fixing build file to include livewidget sources...")
extra_sources = [cp for cp in glob.glob("../*.cpp")
                 if not cp.startswith("../moc_")]
extra_headers = glob.glob("../*.h")
extra_moc_headers = []
for header in extra_headers:
    text = open(header).read()
    if re.compile(r'^\s*Q_OBJECT', re.M).search(text):
        extra_moc_headers.append(header)
for fn in extra_sources + extra_headers:
    bn = os.path.basename(fn)
    if not os.path.islink(bn):
        os.symlink(fn, bn)
fix_build_file(build_file, map(basename, extra_sources),
               map(basename, extra_headers),
               map(basename, extra_moc_headers))

print("Generating makefile...")
makefile = pyqtconfig.QtGuiModuleMakefile(
    configuration=config, build_file=build_file,
    debug='-r' not in sys.argv)

dist = platform.linux_distribution()[0].strip() # old openSUSE appended a space here :(
if dist == 'openSUSE' :
    makefile.extra_include_dirs = ["/usr/include/qwt5",
                                   "/usr/include/qwt",
                                   "/usr/include/libcfitsio0",
                                   "/usr/include/cfitsio"]
    makefile.extra_libs = ["qwt", "cfitsio"]
elif dist in ['Ubuntu', 'LinuxMint']:
    makefile.extra_include_dirs = ["/usr/include/qwt-qt4"]
    makefile.extra_libs = ["qwt-qt4", "cfitsio"]
elif dist == 'CentOS':
    makefile.extra_include_dirs = ["/usr/local/qwt5/include"]
    makefile.extra_libs = ["qwt", "cfitsio"]
else:
    print("WARNING: Don't know where to find Qwt headers and libraries for your distribution")
    # still try to build with useable defaults
    makefile.extra_include_dirs = ["/usr/include/qwt"]
    makefile.extra_libs = ["qwt", "cfitsio"]

makefile.generate()
