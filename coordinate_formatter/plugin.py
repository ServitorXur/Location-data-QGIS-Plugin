# SPDX-License-Identifier: GPL-2.0-or-later
import os

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCsException,
    QgsProject,
)
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import QAction

from .dock import CoordinateDock

MENU = "&Coordinate Formatter"


class CoordinateFormatter:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None
        self.dock = None
        self.marker = None
        self.map_tool = QgsMapToolEmitPoint(self.canvas)
        self.map_tool.canvasClicked.connect(self.handle_click)

    def initGui(self):
        icon = QIcon(os.path.join(os.path.dirname(__file__), "icon.svg"))
        self.action = QAction(icon, "Coordinate Formatter", self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.setToolTip("Pick a point on the map to show it in decimal, DMS, UTM and MGRS")
        self.action.triggered.connect(self.run)
        self.map_tool.setAction(self.action)  # keeps the button checked only while the tool is active
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(MENU, self.action)

        self.dock = CoordinateDock(self.action, self.iface.mainWindow())
        self.dock.visibilityChanged.connect(self.on_dock_visibility)
        self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.dock.hide()

    def unload(self):
        self.canvas.unsetMapTool(self.map_tool)
        self.remove_marker()
        self.iface.removeDockWidget(self.dock)
        self.dock.deleteLater()
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu(MENU, self.action)

    def run(self, checked):
        if checked:
            self.dock.show()
            self.dock.raise_()
            self.canvas.setMapTool(self.map_tool)
        else:
            self.canvas.unsetMapTool(self.map_tool)

    def handle_click(self, point, _button):
        transform = QgsCoordinateTransform(
            self.canvas.mapSettings().destinationCrs(),
            QgsCoordinateReferenceSystem("EPSG:4326"),
            QgsProject.instance(),
        )
        try:
            wgs = transform.transform(point)
        except QgsCsException:
            self.dock.show_error("This point can't be converted to WGS84 from the map's CRS.")
            return
        if not -90 <= wgs.y() <= 90:
            self.dock.show_error("This point is off the globe.")
            return
        lon = (wgs.x() + 180) % 360 - 180  # wrap canvases panned past the antimeridian
        self.dock.show_point(wgs.y(), lon)
        self.dock.show()
        self.show_marker(point)

    def show_marker(self, point):
        if self.marker is None:
            self.marker = QgsVertexMarker(self.canvas)
            self.marker.setIconType(QgsVertexMarker.ICON_CROSS)
            self.marker.setIconSize(16)
            self.marker.setPenWidth(2)
            self.marker.setColor(QColor("#e8590c"))
        self.marker.setCenter(point)

    def remove_marker(self):
        if self.marker is not None:
            self.canvas.scene().removeItem(self.marker)
            self.marker = None

    def on_dock_visibility(self, visible):
        if not visible:
            self.remove_marker()
