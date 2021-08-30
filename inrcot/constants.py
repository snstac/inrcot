#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""inReach to Cursor-on-Target Constants."""

import logging
import os

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


if bool(os.environ.get('DEBUG')):
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = logging.Formatter(
        ('%(asctime)s inrcot %(levelname)s %(name)s.%(funcName)s:%(lineno)d '
         ' - %(message)s'))
    logging.debug('inrcot Debugging Enabled via DEBUG Environment Variable.')
else:
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = logging.Formatter('%(asctime)s inrcot - %(message)s')

# How long between checking for new messages at the Spot API?
DEFAULT_POLL_INTERVAL: int = 120

# How longer after producting the CoT Event is the Event 'stale' (seconds)
DEFAULT_COT_STALE: int = 600

# CoT Event Type / 2525 type / SIDC-like
DEFAULT_COT_TYPE: str = "a-.-G-E-V-C"
