from qgis.PyQt.QtWidgets import QAction
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import (
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsProject
)

from .coordinate_formatter_dialog import CoordinateFormatterDialog

class CoordinateFormatter:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None

        self.map_tool = QgsMapToolEmitPoint(self.canvas)
        self.map_tool.canvasClicked.connect(self.handle_click)