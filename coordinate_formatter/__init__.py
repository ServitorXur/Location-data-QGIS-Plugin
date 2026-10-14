# SPDX-License-Identifier: GPL-2.0-or-later
"""Coordinate Formatter - a QGIS plugin by Nathan Mackintosh."""


def classFactory(iface):  # pylint: disable=invalid-name
    from .plugin import CoordinateFormatter
    return CoordinateFormatter(iface)
