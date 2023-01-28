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


"""INRCOT Class Definitions."""

import asyncio

from typing import Optional

import aiohttp

import pytak
import inrcot


__author__ = "Greg Albrecht <oss@undef.net>"
__copyright__ = "Copyright 2023 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


class Worker(pytak.QueueWorker):
    """Read inReach Feed, renders to CoT, and puts on a TX queue."""

    def __init__(self, queue: asyncio.Queue, config, orig_config) -> None:
        super().__init__(queue, config)
        self.inreach_feeds: list = inrcot.create_feeds(orig_config)

    async def handle_data(self, data: bytes, feed_conf: dict) -> None:
        """Handle the response from the inReach API."""
        feeds: Optional[list] = inrcot.split_feed(data)
        if not feeds:
            return None
        for feed in feeds:
            event: Optional[bytes] = inrcot.inreach_to_cot(feed, feed_conf)
            if not event:
                self._logger.debug("Empty CoT Event")
                continue
            await self.put_queue(event)

    async def get_inreach_feeds(self) -> None:
        """Get inReach Feed from API."""
        for feed_conf in self.inreach_feeds:
            feed_auth = feed_conf.get("feed_auth")
            if not feed_auth:
                self._logger.warning("No feed_auth specified.")
                continue

            feed_url = feed_conf.get("feed_url")
            if not feed_url:
                self._logger.warning("No feed_url specified.")
                continue

            async with aiohttp.ClientSession() as session:
                try:
                    response = await session.request(
                        method="GET", auth=feed_auth, url=feed_url
                    )
                except Exception as exc:  # NOQA pylint: disable=broad-except
                    self._logger.warning("Exception raised while polling inReach API.")
                    self._logger.exception(exc)
                    continue

                status: int = response.status
                if status != 200:
                    self._logger.warning(
                        "No valid response from inReach API: status=%s", status
                    )
                    self._logger.debug(response)
                    continue

                await self.handle_data(await response.content.read(), feed_conf)

    async def run(self, number_of_iterations=-1) -> None:
        """Run this Worker, Reads from Pollers."""
        self._logger.info("Run: %s", self.__class__)

        poll_interval: int = int(
            self.config.get("POLL_INTERVAL", inrcot.DEFAULT_POLL_INTERVAL)
        )

        while 1:
            await self.get_inreach_feeds()
            await asyncio.sleep(poll_interval)
