import os
from distutils.core import setup
from distutils.util import convert_path

def find_packages():
    """Return a list of all nicm subpackages."""
    out = []
    stack = [('nicm', 'nicm/')]
    while stack:
        where, prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if '.' not in name and os.path.isdir(fn) and \
                    os.path.isfile(os.path.join(fn, '__init__.py')):
                out.append(prefix + name)
                stack.append((fn, prefix + name + '.'))
    return out

import nicm

scripts = ['bin/' + name for name in os.listdir('bin')
           if name.startswith('nicm-')]

setup(
    name='nicm',
    version=nicm.__version__,
    license='BSD',
    author='Jens Krueger',
    author_email='jens.krueger@frm2.tum.de',
    description='Network Instrument Control Methods',
    packages=find_packages(),
#    ext_modules=[],
    scripts=scripts,
    data_files=[('/etc', ['etc/nicm.conf'])],
)
