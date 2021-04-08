from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.utils import findResource


class TestPanel(Panel):
    panelName = 'test'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self,
               findResource('nicos_ess/loki/gui/ui_files/form.ui')
               )
