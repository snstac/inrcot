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

"""PyTAK Command Line."""

import argparse
import asyncio
import importlib
import logging
import os
import platform
import pprint
import sys
import warnings

from configparser import ConfigParser, SectionProxy

import pytak

# Python 3.6 support:
if sys.version_info[:2] >= (3, 7):
    from asyncio import get_running_loop
else:
    warnings.warn("Using Python < 3.7, consider upgrading Python.")
    from asyncio import get_event_loop as get_running_loop

__author__ = "Greg Albrecht <oss@undef.net>"
__copyright__ = "Copyright 2023 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


async def main(
    app_name: str, config: SectionProxy, original_config: ConfigParser
) -> None:
    """
    Abstract implementation of an async main function.

    Parameters
    ----------
    app_name : `str`
        Name of the app calling this function.
    config : `SectionProxy`
        A dict of configuration parameters & values.
    """
    app = importlib.__import__(app_name)
    clitool: pytak.CLITool = pytak.CLITool(config)
    create_tasks = getattr(app, "create_tasks")
    await clitool.setup()
    clitool.add_tasks(create_tasks(config, clitool, original_config))
    await clitool.run()


def cli(app_name: str = "inrcot") -> None:
    """
    Abstract implementation of a Command Line Interface (CLI).

    Parameters
    ----------
    app_name : `str`
        Name of the app calling this function.
    """
    app = importlib.__import__(app_name)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--CONFIG_FILE",
        dest="CONFIG_FILE",
        default="config.ini",
        type=str,
        help="Optional configuration file. Default: config.ini",
    )
    parser.add_argument(
        "-p",
        "--PREF_PACKAGE",
        dest="PREF_PACKAGE",
        required=False,
        type=str,
        help="Optional connection preferences package zip file (aka data package).",
    )
    namespace = parser.parse_args()
    cli_args = {k: v for k, v in vars(namespace).items() if v is not None}

    # Read config:
    env_vars = os.environ

    # Remove env vars that contain '%', which ConfigParser or pprint barf on:
    env_vars = {key: val for key, val in env_vars.items() if "%" not in val}

    env_vars["COT_URL"] = env_vars.get("COT_URL", pytak.DEFAULT_COT_URL)
    env_vars["COT_HOST_ID"] = f"{app_name}@{platform.node()}"
    env_vars["COT_STALE"] = getattr(app, "DEFAULT_COT_STALE", pytak.DEFAULT_COT_STALE)

    orig_config: ConfigParser = ConfigParser(env_vars)

    config_file = cli_args.get("CONFIG_FILE")
    if config_file and os.path.exists(config_file):
        logging.info("Reading configuration from %s", config_file)
        orig_config.read(config_file)
    else:
        orig_config.add_section(app_name)

    config: SectionProxy = orig_config[app_name]

    pref_package: str = config.get("PREF_PACKAGE", cli_args.get("PREF_PACKAGE"))
    if pref_package and os.path.exists(pref_package):
        pref_config = pytak.read_pref_package(pref_package)
        config.update(pref_config)

    debug = config.getboolean("DEBUG")
    if debug:
        print(f"Showing Config: {config_file}")
        print("=" * 10)
        pprint.pprint(dict(config))
        print("=" * 10)

    if sys.version_info[:2] >= (3, 7):
        asyncio.run(main(app_name, config, orig_config), debug=debug)
    else:
        loop = get_running_loop()
        try:
            loop.run_until_complete(main(app_name, config, orig_config))
        finally:
            loop.close()
