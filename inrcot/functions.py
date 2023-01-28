#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2023 Greg Albrecht <oss@undef.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""INRCOT Gateway Functions."""

import datetime
import io
import xml.etree.ElementTree as ET

from configparser import ConfigParser
from typing import Optional, Set

from aiohttp import BasicAuth

import pytak
import inrcot


__author__ = "Greg Albrecht <oss@undef.net>"
__copyright__ = "Copyright 2023 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


def create_tasks(
    config: ConfigParser, clitool: pytak.CLITool, original_config: ConfigParser
) -> Set[pytak.Worker,]:
    """Create specific coroutine task set for this application.

    Parameters
    ----------
    config : `ConfigParser`
        Configuration options & values.
    clitool : `pytak.CLITool`
        A PyTAK Worker class instance.

    Returns
    -------
    `set`
        Set of PyTAK Worker classes for this application.
    """
    return set([inrcot.Worker(clitool.tx_queue, config, original_config)])


def split_feed(content: bytes) -> Optional[list]:
    """Split an inReach MapShare KML feed by 'Folder'."""
    tree = ET.parse(io.BytesIO(content))
    document = tree.find("{http://www.opengis.net/kml/2.2}Document")
    if not document:
        return None
    folder = document.findall("{http://www.opengis.net/kml/2.2}Folder")
    return folder


def make_feed_conf(section) -> dict:
    """Make a feed conf dictionary from a conf."""
    feed_conf: dict = {
        "feed_url": section.get("FEED_URL"),
        "cot_stale": section.get("COT_STALE", inrcot.DEFAULT_COT_STALE),
        "cot_type": section.get("COT_TYPE", inrcot.DEFAULT_COT_TYPE),
        "cot_icon": section.get("COT_ICON"),
        "cot_name": section.get("COT_NAME"),
    }
    # Support "private" MapShare feeds:
    feed_pass: str = section.get("FEED_PASSWORD")
    feed_user: str = section.get("FEED_USERNAME")
    if feed_pass and feed_user:
        feed_auth: BasicAuth = BasicAuth(feed_user, feed_pass)
        feed_conf["feed_auth"] = str(feed_auth)

    return feed_conf


def create_feeds(config: ConfigParser) -> list:
    """Create a list of feed configurations."""
    feeds: list = []
    for feed in config.sections():
        if not "inrcot_feed_" in feed:
            continue
        config_section = config[feed]
        feed_conf: dict = make_feed_conf(config_section)
        feed_conf["feed_name"] = feed
        feeds.append(feed_conf)
    return feeds


def inreach_to_cot_xml(
    feed: str, feed_conf: Optional[dict] = None
) -> Optional[ET.Element]:
    """Convert an inReach Response to a Cursor-on-Target Event, as an XML Obj."""
    feed_conf = feed_conf or {}

    placemarks = feed.find("{http://www.opengis.net/kml/2.2}Placemark")
    _point = placemarks.find("{http://www.opengis.net/kml/2.2}Point")
    coordinates = _point.find("{http://www.opengis.net/kml/2.2}coordinates").text
    _name = placemarks.find("{http://www.opengis.net/kml/2.2}name").text

    ts = placemarks.find("{http://www.opengis.net/kml/2.2}TimeStamp")
    when = ts.find("{http://www.opengis.net/kml/2.2}when").text

    if not "," in coordinates or coordinates.count(",") != 2:
        return None

    lon, lat, alt = coordinates.split(",")
    if not all([lat, lon]):
        return None

    time = when

    # We want to use localtime + stale instead of lastUpdate time + stale
    # This means a device could go offline and we might not know it?
    _cot_stale = feed_conf.get("cot_stale", inrcot.DEFAULT_COT_STALE)
    cot_stale = (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=int(_cot_stale))
    ).strftime(pytak.ISO_8601_UTC)

    cot_type = feed_conf.get("cot_type", inrcot.DEFAULT_COT_TYPE)

    name = feed_conf.get("cot_name") or _name
    callsign = name

    point = ET.Element("point")
    point.set("lat", str(lat))
    point.set("lon", str(lon))
    point.set("hae", "9999999.0")
    point.set("ce", "9999999.0")
    point.set("le", "9999999.0")

    contact = ET.Element("contact")
    contact.set("callsign", f"{callsign} (inReach)")

    detail = ET.Element("detail")
    detail.append(contact)

    remarks = ET.Element("remarks")

    _remarks = f"Garmin inReach User.\r\n Name: {name}"

    detail.set("remarks", _remarks)
    remarks.text = _remarks
    detail.append(remarks)

    cot_icon: Optional[str] = feed_conf.get("cot_icon")
    if cot_icon:
        usericon = ET.Element("usericon")
        usericon.set("iconsetpath", cot_icon)
        detail.append(usericon)

    root = ET.Element("event")
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


def inreach_to_cot(content: str, feed_conf: Optional[dict] = None) -> Optional[bytes]:
    """Render a CoT XML as a string."""
    cot: Optional[ET.Element] = inreach_to_cot_xml(content, feed_conf)
    return ET.tostring(cot) if cot else None
