#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# inReach to Cursor-on-Target Gateway.

"""
inReach to Cursor-on-Target Gateway.
~~~~

:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2021 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/inrcot>
"""

from .constants import (LOG_FORMAT, LOG_LEVEL, DEFAULT_POLL_INTERVAL,  # NOQA
                        DEFAULT_COT_STALE, DEFAULT_COT_TYPE)

from .functions import inreach_to_cot, split_feed  # NOQA

from .classes import InrWorker  # NOQA

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
