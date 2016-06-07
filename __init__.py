# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ElevationPlugin
                                 A QGIS plugin
 QGIS Python plugin to download global terrain digital elevation models, SRTM 30m DEM and SRTM 90m DEM.
                             -------------------
        begin                : 2016-06-03
        copyright            : (C) 2016 by B-Open Solutions s.r.l
        email                : office@bopen.eu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ElevationPlugin class from file ElevationPlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qgis_elevation_plugin import ElevationPlugin
    return ElevationPlugin(iface)
