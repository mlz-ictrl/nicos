import os
from distutils.core import setup, Extension

def find_packages():
    """Return a list of all nicos subpackages."""
    out = ['nicos']
    stack = [('nicos', 'nicos/')]
    while stack:
        where, prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if '.' not in name and os.path.isdir(fn) and \
                    os.path.isfile(os.path.join(fn, '__init__.py')):
                out.append(prefix + name)
                stack.append((fn, prefix + name + '.'))
    return out

import nicos

scripts = ['bin/' + name for name in os.listdir('bin')
           if name.startswith('nicos-')]

setup(
    name='nicos-ng',
    version=nicos.__version__,
    license='GPL',
    author='Jens Krueger',
    author_email='jens.krueger@frm2.tum.de',
    description='The Networked Instrument COntrol System of the FRM-II',
    packages=find_packages(),
    ext_modules=[Extension('nicos.daemon._pyctl', ['nicos/daemon/_pyctl.c'])],
    scripts=scripts,
)
