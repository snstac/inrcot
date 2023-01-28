#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""inReach to Cursor-on-Target Gateway Function Tests."""

from configparser import ConfigParser, SectionProxy
from aiohttp import BasicAuth

import unittest

import inrcot.functions

__author__ = "Greg Albrecht <oss@undef.net>"
__copyright__ = "Copyright 2023 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


class FunctionsTestCase(unittest.TestCase):
    """Test for inrcot Functions."""

    def test_inreach_to_cot_xml(self):
        """Test rendering inReach KML a Python XML Object."""
        with open("tests/data/test.kml", "rb") as test_kml_fd:
            test_kml_feed = test_kml_fd.read()

        test_kml = inrcot.functions.split_feed(test_kml_feed)[0]
        test_cot = inrcot.functions.inreach_to_cot_xml(test_kml, {})

        point = test_cot.find("point")

        self.assertEqual(test_cot.get("type"), "a-f-g-e-s")
        self.assertEqual(test_cot.get("uid"), "Garmin-inReach.GregAlbrecht")
        self.assertEqual(point.get("lat"), "33.874926")
        self.assertEqual(point.get("lon"), "-118.346915")

    def test_inreach_to_cot(self):
        """Test rendering inReach KML as a Python XML String."""
        with open("tests/data/test.kml", "rb") as test_kml_fd:
            test_kml_feed = test_kml_fd.read()

        test_kml = inrcot.functions.split_feed(test_kml_feed)[0]
        test_cot = inrcot.functions.inreach_to_cot(test_kml, {})

        self.assertIn(b"Greg Albrecht (inReach)", test_cot)

    def test_inreach_to_cot_xml_from_config(self):
        """Test rendering inReach KML a Python XML Object."""
        with open("tests/data/test.kml", "rb") as test_kml_fd:
            test_kml_feed = test_kml_fd.read()

        test_config_file = "tests/data/test-config.ini"
        orig_config: ConfigParser = ConfigParser()
        orig_config.read(test_config_file)
        feeds = inrcot.functions.create_feeds(orig_config)

        test_kml = inrcot.functions.split_feed(test_kml_feed)[0]
        test_cot = inrcot.functions.inreach_to_cot_xml(test_kml, feeds[0])

        point = test_cot.find("point")
        detail = test_cot.find("detail")
        usericon = detail.find("usericon")

        self.assertEqual(test_cot.get("type"), "a-f-G-U-C")
        self.assertEqual(test_cot.get("uid"), "Garmin-inReach.GregAlbrecht")
        self.assertEqual(point.get("lat"), "33.874926")
        self.assertEqual(point.get("lon"), "-118.346915")
        self.assertEqual(usericon.get("iconsetpath"), "TACOS/taco.png")

    def test_inreach_to_cot_from_config(self):
        """Test rendering inReach KML as a Python XML String."""
        with open("tests/data/test.kml", "rb") as test_kml_fd:
            test_kml_feed = test_kml_fd.read()

        test_config_file = "tests/data/test-config.ini"
        orig_config: ConfigParser = ConfigParser()
        orig_config.read(test_config_file)
        feeds = inrcot.functions.create_feeds(orig_config)

        test_kml = inrcot.functions.split_feed(test_kml_feed)[0]
        test_cot = inrcot.functions.inreach_to_cot(test_kml, feeds[0])

        self.assertIn(b"Greg Albrecht (inReach)", test_cot)

    def test_create_feeds(self):
        """Test creating feeds from config."""
        test_config_file = "tests/data/test-config.ini"
        orig_config: ConfigParser = ConfigParser()
        orig_config.read(test_config_file)

        # config: SectionProxy = orig_config["inrcot"]

        feeds = inrcot.functions.create_feeds(orig_config)
        self.assertTrue(len(feeds) == 6)
        feed = feeds[0]
        self.assertEqual(feed["feed_name"], "inrcot_feed_1")
        self.assertEqual(feed.get("cot_type"), "a-f-G-U-C")
        self.assertEqual(feed["cot_type"], "a-f-G-U-C")
        self.assertEqual(
            feed["feed_url"], "https://share.garmin.com/Feed/Share/ampledata"
        )
        self.assertEqual(feed["cot_stale"], "600")
        self.assertEqual(feed["cot_icon"], "TACOS/taco.png")
        self.assertEqual(feed["cot_name"], None)

    def test_create_feeds_with_auth(self):
        """Test creating feeds with auth from config."""
        test_config_file = "tests/data/test-config.ini"
        orig_config: ConfigParser = ConfigParser()
        orig_config.read(test_config_file)

        feeds = inrcot.functions.create_feeds(orig_config)
        self.assertTrue(len(feeds) == 6)
        feed = feeds[5]
        self.assertEqual(feed["feed_name"], "inrcot_feed_ppp")
        self.assertEqual(feed.get("cot_type"), "a-f-g-e-s")
        self.assertEqual(feed["cot_type"], "a-f-g-e-s")
        self.assertEqual(feed["feed_url"], "https://share.garmin.com/Feed/Share/ppp")
        self.assertEqual(feed["cot_stale"], "600")
        self.assertEqual(feed["cot_icon"], None)
        self.assertEqual(feed["cot_name"], None)
        self.assertEqual(
            feed["feed_auth"],
            "BasicAuth(login='secretsquirrel', password='supersecret', encoding='latin1')",
        )

    def test_inreach_to_cot_xml_bad_kml(self):
        """Test rendering bad KML."""
        with open("tests/data/bad.kml", "rb") as test_kml_fd:
            test_kml_feed = test_kml_fd.read()

        test_kml = inrcot.functions.split_feed(test_kml_feed)
        self.assertEqual(test_kml, None)

    def test_inreach_to_cot_xml_bad_data(self):
        """Test rendering bad KML."""
        with open("tests/data/bad-data.kml", "rb") as test_kml_fd:
            test_kml_feed = test_kml_fd.read()

        test_kml = inrcot.functions.split_feed(test_kml_feed)[0]
        test_cot = inrcot.functions.inreach_to_cot(test_kml, {})
        self.assertEqual(test_cot, None)

    def test_inreach_to_cot_xml_bad_data2(self):
        """Test rendering bad KML."""
        with open("tests/data/bad-data2.kml", "rb") as test_kml_fd:
            test_kml_feed = test_kml_fd.read()

        test_kml = inrcot.functions.split_feed(test_kml_feed)[0]
        test_cot = inrcot.functions.inreach_to_cot(test_kml, {})
        self.assertEqual(test_cot, None)


if __name__ == "__main__":
    unittest.main()
