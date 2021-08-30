#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""inReach Cursor-on-Target Class Definitions."""

import asyncio

import aiohttp

import pytak

import inrcot

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


class InrWorker(pytak.MessageWorker):

    """Reads inReach Data, renders to CoT, and puts on queue."""

    def __init__(self, event_queue: asyncio.Queue, config) -> None:
        super().__init__(event_queue)

        # self.cot_stale = opts.get("COT_STALE")
        # self.cot_type = opts.get("COT_TYPE") or inrcot.DEFAULT_COT_TYPE

        self.poll_interval: int = int(config["inrcot"].get(
            "POLL_INTERVAL", inrcot.DEFAULT_POLL_INTERVAL))

        # Used by inreach_to_cot function:
        self.cot_renderer = inrcot.inreach_to_cot

        self.inreach_feeds: list = []

        for feed in config.sections():
            if "inrcot_feed_" in feed:
                self.inreach_feeds.append({
                    "feed_url": config[feed].get("FEED_URL"),
                    "cot_stale": config[feed].get(
                        "COT_STALE", inrcot.DEFAULT_COT_STALE),
                    "cot_type": config[feed].get(
                        "COT_TYPE", inrcot.DEFAULT_COT_TYPE),
                    "cot_icon": config[feed].get("COT_ICON"),
                    "cot_name": config[feed].get("COT_NAME"),
                })

    async def handle_response(self, content: str, feed_conf: dict) -> None:
        """Handles the response from the inReach API."""
        event: str = inrcot.inreach_to_cot(content, feed_conf)
        if event:
            await self._put_event_queue(event)
        else:
            self._logger.debug("Empty CoT Event")

    async def _get_inreach_feeds(self):
        """Gets inReach Feed from API."""
        self._logger.debug("Polling inReach API")

        for feed_conf in self.inreach_feeds:
            async with aiohttp.ClientSession() as session:
                try:
                    response = await session.request(
                        method="GET", url=feed_conf.get("feed_url"))
                except Exception as exc:  # NOQA pylint: disable=broad-except
                    self._logger.error(
                        "Exception raised while polling inReach API.")
                    self._logger.exception(exc)
                    return

                if response.status == 200:
                    await self.handle_response(await response.content.read(),
                                               feed_conf)
                else:
                    self._logger.error("No valid response from inReach API.")

    async def run(self) -> None:
        """Runs this Worker, Reads from Pollers."""
        self._logger.info("Running InrWorker")

        while 1:
            await self._get_inreach_feeds()
            await asyncio.sleep(self.poll_interval)
