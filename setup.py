import os, sys
from distutils.core import setup, Extension
from distutils.command.install import install

def find_packages():
    """Return a list of all nicos subpackages."""
    out = ['nicos']
    stack = [('lib/nicos', 'nicos.')]
    while stack:
        where, prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if '.' not in name and os.path.isdir(fn) and \
                    os.path.isfile(os.path.join(fn, '__init__.py')):
                out.append(prefix + name)
                stack.append((fn, prefix + name + '.'))
    return out

sys.path.append('lib')
import nicos

scripts = ['bin/' + name for name in os.listdir('bin')
           if name.startswith('nicos-')]

class no_install(install):
    def initialize_options(self):
        print 'Please use "make install" to install nicos-ng.'
        sys.exit(1)

setup(
    name='nicos-ng',
    version=nicos.__version__,
    license='GPL',
    author='Jens Krueger',
    author_email='jens.krueger@frm2.tum.de',
    description='The Networked Instrument COntrol System of the FRM-II',
    package_dir={'': 'lib'},
    packages=find_packages(),
    ext_modules=[Extension('nicos.daemon._pyctl', ['src/_pyctl.c'])],
    scripts=scripts,
    cmdclass={'install': no_install},
    package_data={'nicos.web': ['jquery.js', 'support.js']},
    # XXX: add the .ui files for the GUI!
)
