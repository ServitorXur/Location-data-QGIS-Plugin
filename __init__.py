self.map_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
self.map_tool.canvasClicked.connect(self.handle_click)
