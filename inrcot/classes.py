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

"""INRCOT Class Definitions."""

import asyncio

import aiohttp

import pytak
import inrcot


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


class Worker(pytak.QueueWorker):

    """Reads inReach Feed, renders to CoT, and puts on a TX queue."""

    def __init__(self, queue: asyncio.Queue, config, original_config) -> None:
        super().__init__(queue, config)
        self.inreach_feeds: list = []
        self._create_feeds(original_config)

    def _create_feeds(self, config: dict = None) -> None:
        """Creates a list of feed configurations."""
        for feed in config.sections():
            if "inrcot_feed_" in feed:
                feed_conf = {
                    "feed_url": config[feed].get("FEED_URL"),
                    "cot_stale": config[feed].get(
                        "COT_STALE", inrcot.DEFAULT_COT_STALE
                    ),
                    "cot_type": config[feed].get("COT_TYPE", inrcot.DEFAULT_COT_TYPE),
                    "cot_icon": config[feed].get("COT_ICON"),
                    "cot_name": config[feed].get("COT_NAME"),
                }

                # Support "private" MapShare feeds:
                if config[feed].get("FEED_PASSWORD") and config[feed].get(
                    "FEED_USERNAME"
                ):
                    feed_conf["feed_auth"] = aiohttp.BasicAuth(
                        config[feed].get("FEED_USERNAME"),
                        config[feed].get("FEED_PASSWORD"),
                    )

                self.inreach_feeds.append(feed_conf)

    async def handle_data(self, data: str, feed_conf: dict) -> None:
        """Handles the response from the inReach API."""
        for feed in inrcot.split_feed(data):
            event: str = inrcot.inreach_to_cot(feed, feed_conf)
            if event:
                await self.put_queue(event)
            else:
                self._logger.debug("Empty COT Event")

    async def get_inreach_feeds(self):
        """Gets inReach Feed from API."""
        for feed_conf in self.inreach_feeds:
            feed_auth = feed_conf.get("feed_auth")
            async with aiohttp.ClientSession() as session:
                try:
                    response = await session.request(
                        method="GET", auth=feed_auth, url=feed_conf.get("feed_url")
                    )
                except Exception as exc:  # NOQA pylint: disable=broad-except
                    self._logger.error("Exception raised while polling inReach API.")
                    self._logger.exception(exc)
                    return

                if response.status == 200:
                    await self.handle_data(await response.content.read(), feed_conf)
                else:
                    self._logger.error("No valid response from inReach API.")

    async def run(self) -> None:
        """Runs this Worker, Reads from Pollers."""
        self._logger.info("Run: %s", self.__class__)

        poll_interval: str = self.config.get(
            "POLL_INTERVAL", inrcot.DEFAULT_POLL_INTERVAL
        )

        while 1:
            await self.get_inreach_feeds()
            await asyncio.sleep(int(poll_interval))
