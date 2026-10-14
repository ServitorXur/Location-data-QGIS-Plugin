# SPDX-License-Identifier: GPL-2.0-or-later
"""Pure-Python WGS84 coordinate formatting: decimal, DMS, UTM and MGRS.

No QGIS imports, so this module can be unit tested on its own.
"""
import math

_A = 6378137.0
_F = 1 / 298.257223563
_K0 = 0.9996
_BANDS = "CDEFGHJKLMNPQRSTUVWX"
_MGRS_COLS = ("ABCDEFGH", "JKLMNPQR", "STUVWXYZ")
_MGRS_ROWS = "ABCDEFGHJKLMNPQRSTUV"


def to_decimal(lat, lon):
    return f"{lat:.6f}, {lon:.6f}"


def _dms(value, pos, neg):
    # Round once in hundredths of a second so 59.999" carries into the minute.
    total = round(abs(value) * 360000)
    deg, rest = divmod(total, 360000)
    minutes, hsec = divmod(rest, 6000)
    return f"{deg}°{minutes:02d}'{hsec / 100:05.2f}\"{pos if value >= 0 else neg}"


def to_dms(lat, lon):
    return f"{_dms(lat, 'N', 'S')} {_dms(lon, 'E', 'W')}"


def utm_zone(lat, lon):
    if 56 <= lat < 64 and 3 <= lon < 12:
        return 32  # Norway exception
    if 72 <= lat < 84 and 0 <= lon < 42:
        return (31, 33, 35, 37)[min(int((lon + 3) // 12), 3)]  # Svalbard exception
    return min(int((lon + 180) // 6) + 1, 60)


def to_utm(lat, lon):
    """Return (zone, band, easting, northing), or None outside UTM's 80°S-84°N range."""
    if not -80 <= lat <= 84:
        return None
    zone = utm_zone(lat, lon)
    band = _BANDS[min(int((lat + 80) // 8), 19)]

    # Krüger series (Karney 2011), sub-millimetre accurate within a zone.
    n = _F / (2 - _F)
    big_a = _A / (1 + n) * (1 + n ** 2 / 4 + n ** 4 / 64)
    alpha = (n / 2 - 2 * n ** 2 / 3 + 5 * n ** 3 / 16,
             13 * n ** 2 / 48 - 3 * n ** 3 / 5,
             61 * n ** 3 / 240)
    phi = math.radians(lat)
    dlam = math.radians(lon - (zone * 6 - 183))
    e = 2 * math.sqrt(n) / (1 + n)
    t = math.sinh(math.atanh(math.sin(phi)) - e * math.atanh(e * math.sin(phi)))
    xi = math.atan2(t, math.cos(dlam))
    eta = math.atanh(math.sin(dlam) / math.sqrt(1 + t * t))
    x, y = eta, xi
    for j, a in enumerate(alpha, 1):
        x += a * math.cos(2 * j * xi) * math.sinh(2 * j * eta)
        y += a * math.sin(2 * j * xi) * math.cosh(2 * j * eta)
    easting = 500000 + _K0 * big_a * x
    northing = _K0 * big_a * y + (10000000 if lat < 0 else 0)
    return zone, band, easting, northing


def format_utm(lat, lon):
    utm = to_utm(lat, lon)
    if utm is None:
        return "Outside UTM range (80°S to 84°N)"
    zone, band, e, n = utm
    return f"{zone}{band} {e:.0f}E {n:.0f}N"


def to_mgrs(lat, lon):
    """1 m precision MGRS (WGS84 / AA lettering scheme)."""
    utm = to_utm(lat, lon)
    if utm is None:
        return "Outside MGRS UTM range (80°S to 84°N)"
    zone, band, e, n = utm
    col = _MGRS_COLS[(zone - 1) % 3][int(e // 100000) - 1]
    row = _MGRS_ROWS[(int(n // 100000) + (5 if zone % 2 == 0 else 0)) % 20]
    # MGRS truncates rather than rounds.
    return f"{zone}{band} {col}{row} {int(e % 100000):05d} {int(n % 100000):05d}"
