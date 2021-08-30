#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""inReach to Cursor-on-Target Gateway Function Tests."""

import unittest

import inrcot.functions

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


class FunctionsTestCase(unittest.TestCase):
    """
    Tests for Functions.
    """

    def test_inreach_to_cot_xml(self):
        with open("tests/test.kml", "r") as test_kml_fd:
            test_kml = test_kml_fd.read()

        test_cot = inrcot.functions.inreach_to_cot_xml(test_kml, {})
        point = test_cot.find("point")

        self.assertEqual(test_cot.get("type"), "a-.-G-E-V-C")
        self.assertEqual(test_cot.get("uid"), "Garmin-inReach.GregAlbrecht")
        self.assertEqual(point.get("lat"), "33.874926")
        self.assertEqual(point.get("lon"), "-118.346915")

    def test_inreach_to_cot(self):
        with open("tests/test.kml", "r") as test_kml_fd:
            test_kml = test_kml_fd.read()

        test_cot = inrcot.functions.inreach_to_cot(test_kml, {})

        self.assertIn(b"Greg Albrecht (inReach)", test_cot)


if __name__ == "__main__":
    unittest.main()
