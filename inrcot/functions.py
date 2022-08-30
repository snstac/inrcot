#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Greg Albrecht <oss@undef.net>
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
# Author:: Greg Albrecht W2GMD <oss@undef.net>
#

"""SpotCOT Gateway Functions."""

import datetime
import io
import xml.etree.ElementTree as ET

from configparser import ConfigParser
from typing import Union, Set

import pytak
import inrcot


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


def create_tasks(
    config: ConfigParser, clitool: pytak.CLITool, original_config: ConfigParser
) -> Set[pytak.Worker,]:
    """
    Creates specific coroutine task set for this application.

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


def split_feed(content: str) -> list:
    """Splits an inReach MapShare KML feed by 'Folder'"""
    tree = ET.parse(io.BytesIO(content))
    document = tree.find("{http://www.opengis.net/kml/2.2}Document")
    folder = document.findall("{http://www.opengis.net/kml/2.2}Folder")
    return folder


def inreach_to_cot_xml(feed: str, feed_conf: dict = None) -> Union[ET.Element, None]:
    """
    Converts an inReach Response to a Cursor-on-Target Event, as an XML Obj.
    """
    feed_conf = feed_conf or {}

    placemarks = feed.find("{http://www.opengis.net/kml/2.2}Placemark")
    _point = placemarks.find("{http://www.opengis.net/kml/2.2}Point")
    coordinates = _point.find("{http://www.opengis.net/kml/2.2}coordinates").text
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

    uid = ET.Element("UID")
    uid.set("Droid", f"{name} (inReach)")

    contact = ET.Element("contact")
    contact.set("callsign", f"{callsign} (inReach)")

    track = ET.Element("track")
    track.set("course", "9999999.0")

    detail = ET.Element("detail")
    detail.set("uid", name)
    detail.append(uid)
    detail.append(contact)
    detail.append(track)

    remarks = ET.Element("remarks")

    _remarks = f"Garmin inReach User.\r\n Name: {name}"

    detail.set("remarks", _remarks)
    remarks.text = _remarks
    detail.append(remarks)

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


def inreach_to_cot(content: str, feed_conf: dict = None) -> Union[bytes, None]:
    """Wrapper that returns COT as an XML string."""
    cot: Union[ET.Element, None] = inreach_to_cot_xml(content, feed_conf)
    return ET.tostring(cot) if cot else None
