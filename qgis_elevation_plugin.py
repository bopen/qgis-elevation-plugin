# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ElevationPlugin
                                 A QGIS plugin
 QGIS Python plugin to download global terrain digital elevation models, SRTM 30m DEM and SRTM 90m DEM.
                              -------------------
        begin                : 2016-06-03
        git sha              : $Format:%H$
        copyright            : (C) 2016 by B-Open Solutions s.r.l
        email                : office@bopen.eu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources

from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPoint
from qgis.gui import QgsMessageBar
from qgis import utils

import os.path
import subprocess
import sys
import pip

from qgis_elevation_plugin_dialog import ElevationPluginDialog


def bounds_from_extent(extent, src_crs):
    btm_left = (extent.xMinimum(), extent.yMinimum())
    top_right = (extent.xMaximum(), extent.yMaximum())
    dest_crs = QgsCoordinateReferenceSystem(4326)
    return coords_xform(src_crs, dest_crs, btm_left), coords_xform(src_crs, dest_crs, top_right)


def coords_xform(src_crs, dest_crs, src_point):
    xform = QgsCoordinateTransform(src_crs, dest_crs)
    return xform.transform(QgsPoint(src_point[0], src_point[1]))


class ElevationPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        self.elevation_dir = os.path.join(self.plugin_dir, 'elevation')
        print self.elevation_dir

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ElevationPluginDialog()
        self.dlg.choose_dir_button.clicked.connect(self.open_browse)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QGIS Elevation Plugin')

        # Making GDAL visible
        local_path = '/usr/local/bin:'
        if local_path not in os.environ['PATH']:
            os.environ['PATH'] = local_path + os.environ['PATH']

        # Checking the presence of elevation library
        try:
            import elevation
            print elevation.util.selfcheck(elevation.datasource.TOOLS)
        except:
            self.clear_and_push_message("Installing elevation library!", QgsMessageBar.WARNING, 10)
            pip.main(['install', '--target=%s' % self.elevation_dir, 'elevation'])
            if self.elevation_dir not in sys.path:
                sys.path.append(self.elevation_dir)
            self.clear_and_push_message("Elevation Library correctly installed!", QgsMessageBar.INFO, 5)
        
    def open_browse(self):
        fname = QFileDialog.getExistingDirectory(self.dlg, "Select Directory")
        self.dlg.lineEdit_6.setText(fname)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ElevationPluginDialogBase', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ElevationPlugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Download Dem for the viewport area'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&QGIS Elevation Plugin'),
                action)

    def clear_and_push_message(self, msg, lvl, time):
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage("Elevation Plugin", self.tr(msg), level=lvl, duration=time)

    def fill_with_bounds(self, btm_left, top_right):
        self.dlg.lineEdit.setText(str(btm_left[0]))
        self.dlg.lineEdit_2.setText(str(btm_left[1]))
        self.dlg.lineEdit_3.setText(str(top_right[0]))
        self.dlg.lineEdit_4.setText(str(top_right[1]))

    def run(self):
        active_layer = self.iface.activeLayer()
        try:
            btm_left, top_right = bounds_from_extent(self.iface.mapCanvas().extent(), active_layer.crs())
        except AttributeError:
            self.clear_and_push_message("No active layer!", QgsMessageBar.CRITICAL, 3)
            print "be sure to have an active layer before starting the plugin"
            return

        self.dlg.show()
        self.fill_with_bounds(btm_left, top_right)
        result = self.dlg.exec_()

        if result:
            self.filename = self.dlg.lineEdit_5.text().replace(" ", "")
            self.dest_path = os.path.join(self.dlg.lineEdit_6.text(), self.filename + '.tif')
            self.bounds = (btm_left[0], btm_left[1], top_right[0], top_right[1])
            self.clear_and_push_message("DEM data is being downloaded, please wait for the process to complete", QgsMessageBar.WARNING, 10)

            import elevation
            elevation.datasource.clip(bounds=self.bounds, output=self.dest_path)

            self.clear_and_push_message("Data correctly downloaded", QgsMessageBar.INFO, 5)
            if self.dlg.preview_checkbox.isChecked():
            	self.iface.addRasterLayer(self.dest_path, '%s srtm dem' % self.filename)
