# SPDX-License-Identifier: GPL-2.0-or-later
from qgis.core import QgsApplication
from qgis.gui import QgsDockWidget
from qgis.PyQt.QtGui import QFontDatabase, QFontMetrics
from qgis.PyQt.QtWidgets import (
    QApplication, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QToolButton,
    QVBoxLayout, QWidget,
)

from .formats import format_utm, to_decimal, to_dms, to_mgrs

FORMATS = (
    ("Decimal", to_decimal),
    ("DMS", to_dms),
    ("UTM", format_utm),
    ("MGRS", to_mgrs),
)
HINT = "Click anywhere on the map to read its coordinates."


class CoordinateDock(QgsDockWidget):
    def __init__(self, pick_action, parent=None):
        super().__init__("Coordinate Formatter", parent)
        self.setObjectName("CoordinateFormatterDock")  # lets QGIS restore its position

        self.hint = QLabel(HINT)
        self.hint.setWordWrap(True)
        pick = QToolButton()
        pick.setDefaultAction(pick_action)
        top = QHBoxLayout()
        top.addWidget(self.hint, 1)
        top.addWidget(pick)

        mono = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        copy_icon = QgsApplication.getThemeIcon("/mActionEditCopy.svg")
        form = QFormLayout()
        self.fields = {}
        for name, _ in FORMATS:
            field = QLineEdit()
            field.setReadOnly(True)
            field.setFont(mono)
            # Widest value is DMS, e.g. 51°30'02.62"N 130°17'43.20"W (28 chars).
            field.setMinimumWidth(QFontMetrics(mono).horizontalAdvance("0" * 30))
            field.setPlaceholderText("—")
            field.setAccessibleName(f"{name} coordinates")
            copy = QToolButton()
            copy.setIcon(copy_icon)
            copy.setToolTip(f"Copy {name}")
            copy.setAccessibleName(f"Copy {name} coordinates")
            copy.clicked.connect(lambda _=False, n=name: self.copy(n))
            row = QHBoxLayout()
            row.addWidget(field)
            row.addWidget(copy)
            form.addRow(name, row)
            self.fields[name] = field

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.addLayout(top)
        layout.addLayout(form)
        layout.addStretch()
        self.setWidget(body)

    def show_point(self, lat, lon):
        for name, fmt in FORMATS:
            self.fields[name].setText(fmt(lat, lon))
        self.hint.setText(HINT)

    def show_error(self, message):
        for field in self.fields.values():
            field.clear()
        self.hint.setText(message)

    def copy(self, name):
        text = self.fields[name].text()
        if text:
            QApplication.clipboard().setText(text)
            self.hint.setText(f"Copied {name} to clipboard.")
