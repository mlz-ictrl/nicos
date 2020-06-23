from os import path

from nicos.guisupport.qt import QIcon

iconspath = 'resources/material/icons/'


def get_icon(icon_name):
    return QIcon(path.join(iconspath, icon_name))
