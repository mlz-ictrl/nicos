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
from nicos.core.device import DeviceMetaInfo, DeviceParInfo, Param
from nicos.core.params import anytype, dictof
from nicos.devices.sample import Sample

def to_mutable(obj):
    if isinstance(obj, dict):
        return {k: to_mutable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return obj.__class__(to_mutable(v) for v in obj)
    return obj

def to_yaml(obj):
    return yaml.dump(to_mutable(obj), sort_keys=False, default_flow_style=False).rstrip()

class AmorSample(Sample):
    """AMOR sample with the additional parameters `orsomodel` and `geometry`

    Conceptually, an orso (open reflectometry standards organisation) model is
    the description of a sample consisting of one or more layers of materials
    with a specified thickness. See <https://www.reflectometry.org/> for more.

    This sample class contains parameters for describing both the `orsomodel` as
    well as the general `geometry` of an example. The former can be conveniently
    populated from different input formats via the `model` method, see its
    docstring for more. The `geometry` is a dictionary of the form
      geometry = {
          "shape": oneof("rectangle", "disc", "wedge", "potato", None),
          "radius": None,
          "size": (None, None)
          }
    with unit = mm and "size" being the (x, y)-extents tuple.
    """
    parameters = {
        'orsomodel': Param('multi-line sample description following ORSO standard',
                           type=dictof(str, anytype), settable=True,
                           userparam=True, category='sample', default={'stack': None},
                           ),
        'stack': Param('Stack line of the orsomodel',
                       type=str, volatile=True
                       ),
        # Must not be categorized as 'sample' to avoid being included twice by the info method.
        'orsomodel_yaml': Param('YAML representation of the orsomodel parameter',
                                volatile=True, settable=False, type=str,
                                ),
        'geometry': Param('Dictionary describing the sample shape and size',
                           type=dictof(str, anytype), settable=True,
                           userparam=True, category='sample', default=dict(),
                           ),
        # Must not be categorized as 'sample' to avoid being included twice by the info method.
        'geometry_yaml': Param('YAML representation of the geometry parameter',
                               volatile=True, settable=False, type=str,
                               ),
        }

    def doInfo(self):
        ret = []

        o = self.orsomodel_yaml
        ret.append(DeviceMetaInfo('orsomodel_yaml', DeviceParInfo(o, o, '', 'sample')))

        g = self.geometry_yaml
        ret.append(DeviceMetaInfo('geometry_yaml', DeviceParInfo(g, g, '', 'sample')))
        return ret

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
        return to_yaml(self.orsomodel)

    def doReadGeometry_Yaml(self):
        return to_yaml(self.geometry)

    def model(self, mdl=None):
        """
        Print the current `orsomodel` or replace it from a supported input.

        Parameters
        ----------
        mdl : str or None, optional
            Source of the model description.

            - If `None` (default), the current `self.orsomodel` is printed as a
            YAML-formatted string.
            - If `mdl` is a string containing at least one `"|"` character, it
            is interpreted as a single-line orso model description (for example,
            ``air | 5 ( Ni 4 | Ti 5 ) | Al2O3``). The string is parsed and the
            resulting model is assigned to `self.orsomodel`.
            - Otherwise, `mdl` is interpreted as the relative path to a YAML
            file rooted at `Exp.scriptpath`. The file must contain an orso model
            description, which is parsed and assigned to `self.orsomodel`. See
            <https://www.reflectometry.org/advanced_and_expert_level/file_format/simple_model>
            for some examples of valid orso models.
        """
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
