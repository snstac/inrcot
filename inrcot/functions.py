#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Spot Cursor-on-Target Gateway Functions."""

import datetime
import io

import xml.etree.ElementTree

import pytak

import inrcot.constants

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


def split_feed(content: str) -> list:
    """Splits an inReach MapShare KML feed by 'Folder'"""
    tree = xml.etree.ElementTree.parse(io.BytesIO(content))

    document = tree.find('{http://www.opengis.net/kml/2.2}Document')
    folder = document.findall("{http://www.opengis.net/kml/2.2}Folder")
    return folder


def inreach_to_cot_xml(feed: str, feed_conf: dict = None) -> \
        [xml.etree.ElementTree, None]:
    """
    Converts an inReach Response to a Cursor-on-Target Event, as an XML Obj.
    """
    feed_conf = feed_conf or {}

    placemarks = feed.find("{http://www.opengis.net/kml/2.2}Placemark")
    _point = placemarks.find("{http://www.opengis.net/kml/2.2}Point")
    coordinates = _point.find(
        "{http://www.opengis.net/kml/2.2}coordinates").text
    _name = placemarks.find("{http://www.opengis.net/kml/2.2}name").text

    ts = placemarks.find("{http://www.opengis.net/kml/2.2}TimeStamp")
    when = ts.find("{http://www.opengis.net/kml/2.2}when").text

    lon, lat, alt = coordinates.split(",")
    if lat is None or lon is None:
        return None

    time = when

    # We want to use localtime + stale instead of lastUpdate time + stale
    # This means a device could go offline and we might not know it?
    _cot_stale = feed_conf.get("cot_stale", inrcot.DEFAULT_COT_STALE)
    cot_stale = (datetime.datetime.now(datetime.timezone.utc) +
                 datetime.timedelta(
                     seconds=int(_cot_stale))).strftime(pytak.ISO_8601_UTC)

    cot_type = feed_conf.get("cot_type", inrcot.DEFAULT_COT_TYPE)

    name = feed_conf.get("cot_name") or _name
    callsign = name

    point = xml.etree.ElementTree.Element("point")
    point.set("lat", str(lat))
    point.set("lon", str(lon))
    point.set("hae", "9999999.0")
    point.set("ce", "9999999.0")
    point.set("le", "9999999.0")

    uid = xml.etree.ElementTree.Element("UID")
    uid.set("Droid", f"{name} (inReach)")

    contact = xml.etree.ElementTree.Element("contact")
    contact.set("callsign", f"{callsign} (inReach)")

    track = xml.etree.ElementTree.Element("track")
    track.set("course", "9999999.0")

    detail = xml.etree.ElementTree.Element("detail")
    detail.set("uid", name)
    detail.append(uid)
    detail.append(contact)
    detail.append(track)

    remarks = xml.etree.ElementTree.Element("remarks")

    _remarks = f"Garmin inReach User.\r\n Name: {name}"

    detail.set("remarks", _remarks)
    remarks.text = _remarks
    detail.append(remarks)

    root = xml.etree.ElementTree.Element("event")
    root.set("version", "2.0")
    root.set("type", cot_type)
    root.set("uid", f"Garmin-inReach.{name}".replace(" ", ""))
    root.set("how", "m-g")
    root.set("time", time)  # .strftime(pytak.ISO_8601_UTC))
    root.set("start", time)  # .strftime(pytak.ISO_8601_UTC))
    root.set("stale", cot_stale)
    root.append(point)
    root.append(detail)

    return root


def inreach_to_cot(content: str, feed_conf: dict = None) -> str:
    """
    Converts an inReach Response to a Cursor-on-Target Event, as a String.
    """
    cot_xml: xml.etree.ElementTree = inreach_to_cot_xml(content, feed_conf)
    return xml.etree.ElementTree.tostring(cot_xml)
