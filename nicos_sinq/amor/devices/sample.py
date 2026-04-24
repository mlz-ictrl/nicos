# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Jochen Stahn <jochen.stahn@psi.ch>
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

from os import path
import yaml

from nicos import session
from nicos.utils import printTable
from nicos.core.device import Param
from nicos.core.params import anytype, dictof
from nicos.devices.sample import Sample

def to_mutable(obj):
    if isinstance(obj, dict):
        return {k: to_mutable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return obj.__class__(to_mutable(v) for v in obj)
    return obj

class AmorSample(Sample):
    """AMOR sample with the additional parameters `model` and `geometry`

    The `model` can be

    - a one-line description of the sample's layer stack
      e.g. `air | 5 ( Ni 4 | Ti 5 ) | Al2O3`
    - a multiline, yaml formatted sample description according to the orso model
      description language.

    A yaml file can be loaded from the `scriptpath` via `Sample.model('<name.yml>')`

    The `geometry` is a dictionary of the form
      geometry = {
          "shape": oneof("rectangle", "disc", "wedge", "strange", None),
          "radius": None,
          "size": (None, None)
          }
    with unit = mm.
    """
    parameters = {
        'orsomodel': Param('multi-line sample description following ORSO standard',
                           type=dictof(str, anytype), settable=True,
                           userparam=True, category='sample', default={'stack': None},
                           ),
        'stack': Param('Stack line of the orsomodel',
                       type=str, volatile=True
                       ),
        'orsomodel_yaml': Param('YAML representation of the orsomodel parameter',
                                volatile=True, settable=False, type=str,
                                category='sample'
                                ),
        'geometry': Param('Dictionary describing the sample shape and size',
                           type=dictof(str, anytype), settable=True,
                           userparam=True, category='sample', default=dict(),
                           ),
        'geometry_yaml': Param('YAML representation of the geometry parameter',
                               volatile=True, settable=False, type=str,
                               category='sample'
                               ),
        }

    def clear(self):
        Sample.clear(self)
        self.orsomodel = {'stack': None}
        self.geometry = dict()

    def _applyParams(self, number, parameters):
        Sample._applyParams(self, number, parameters)
        self.orsomodel = parameters.get('orsomodel', {'stack': None})

    def doReadStack(self):
        return self.orsomodel.get('stack','')

    def doReadOrsomodel_Yaml(self):
        return yaml.dump(to_mutable(self.orsomodel), sort_keys=False,
                         default_flow_style=False).rstrip()

    def model(self, mdl=None):
        if mdl is None:
            if self.stack == '':
                self.log.info('there is no model defined')
            else:
                self.printOrsoSampleModel()
        elif '|' in mdl:
            self.orsomodel = {'stack': mdl}
        else:
            scriptpath = session.experiment.scriptpath
            with open(path.join(scriptpath, mdl), 'r', encoding='utf-8') as _mdl:
                self.orsomodel = yaml.safe_load(_mdl)
                self.printOrsoSampleModel()

    def printOrsoSampleModel(self):
        header = 'orso sample model'
        lines = [[line] for line in self.orsomodel_yaml.split('\n')]
        max_line_len = max(len(line[0]) for line in lines)
        prefixed_spaces = (max_line_len - len(header)) // 2
        printTable([' ' * prefixed_spaces +'orso sample model',], lines, self.log.info)

    def doReadGeometry_Yaml(self):
        return yaml.dump(to_mutable(self.geometry), sort_keys=False,
                         default_flow_style=False).rstrip()
