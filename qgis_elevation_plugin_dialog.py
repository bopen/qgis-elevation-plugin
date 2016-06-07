import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qgis_elevation_plugin_dialog_base.ui'))


class ElevationPluginDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ElevationPluginDialog, self).__init__(parent)

        self.setupUi(self)