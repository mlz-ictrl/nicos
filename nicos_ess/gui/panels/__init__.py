from os import path

from nicos.guisupport.qt import QIcon

from nicostools.setupfiletool.utilities.utilities import getNicosDir

root_path = getNicosDir()
icons_path = path.join(root_path, 'resources', 'material', 'icons')


def get_icon(icon_name):
    return QIcon(path.join(icons_path, icon_name))
