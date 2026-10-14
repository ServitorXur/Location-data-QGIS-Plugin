import unittest

from coordinate_formatter.formats import format_utm, to_dms, to_mgrs, to_utm, utm_zone


class FormatsTest(unittest.TestCase):
    def test_dms_keeps_sign_between_zero_and_minus_one(self):
        self.assertEqual(to_dms(-0.5, -0.5), "0°30'00.00\"S 0°30'00.00\"W")

    def test_dms_rounding_carries_into_minutes(self):
        self.assertEqual(to_dms(10.9999999, 0), "11°00'00.00\"N 0°00'00.00\"E")

    def test_utm_matches_reference(self):  # reference values from pyproj (EPSG:32630)
        zone, band, e, n = to_utm(51.5074, -0.1278)
        self.assertEqual((zone, band), (30, "U"))
        self.assertAlmostEqual(e, 699316.2, delta=0.5)
        self.assertAlmostEqual(n, 5710164.2, delta=0.5)

    def test_zone_exceptions(self):
        self.assertEqual(utm_zone(60, 5), 32)       # Norway
        self.assertEqual(utm_zone(78.2, 15.6), 33)  # Svalbard
        self.assertEqual(utm_zone(0, 180), 60)

    def test_mgrs(self):
        self.assertEqual(to_mgrs(38.8895, -77.0353), "18S UJ 23478 06483")  # Washington Monument
        self.assertEqual(to_mgrs(-33.8568, 151.2153), "56H LH 34900 52288")  # Sydney Opera House
        self.assertEqual(to_mgrs(0, 0), "31N AA 66021 00000")

    def test_polar_points_are_out_of_range(self):
        self.assertIsNone(to_utm(85, 0))
        self.assertIn("Outside", format_utm(-85, 0))
        self.assertIn("Outside", to_mgrs(89, 0))


if __name__ == "__main__":
    unittest.main()
