import os, sys
from distutils.core import setup
from distutils.command.install import install

def find_packages():
    """Return a list of all nicos subpackages."""
    out = ['nicos']
    stack = [('nicos', 'nicos.')]
    while stack:
        where, prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if '.' not in name and os.path.isdir(fn) and \
                    os.path.isfile(os.path.join(fn, '__init__.py')):
                out.append(prefix + name)
                stack.append((fn, prefix + name + '.'))
    return out

def find_ui_files():
    """Find all Qt .ui files in nicos.clients.gui subpackages."""
    res = {}
    for root, _dirs, files in os.walk('nicos/clients/gui'):
        uis = [uifile for uifile in files if uifile.endswith('.ui')]
        if uis:
            res[root.replace('/', '.')] = uis
    return res

import nicos

scripts = ['bin/' + name for name in os.listdir('bin')
           if name.startswith('nicos-')]


class no_install(install):
    def initialize_options(self):
        print('Please use "make install" to install NICOS.')
        sys.exit(1)

package_data = {'nicos.services.web': ['jquery.js', 'support.js'],
                'nicos.clients.gui.tools.calculator_images':
                ['braggfml.png', 'miezefml.png']}
package_data.update(find_ui_files())

setup(
    name = 'nicos',
    version = nicos.nicos_version,
    license = 'GPL',
    author = 'Georg Brandl',
    author_email = 'georg.brandl@frm2.tum.de',
    maintainer = 'Jens Krueger',
    maintainer_email = 'jens.krueger@frm2.tum.de',
    description = 'The Networked Instrument COntrol System of the FRM-II',
    url = 'https://trac.frm2.tum.de/projects/NICOS/',

    cmdclass = {'install': no_install},
    packages = find_packages(),
    package_data = package_data,
    scripts = scripts,
)
