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


"""inReach to Cursor on Target Gateway.

:author: Greg Albrecht <oss@undef.net>
:copyright: Copyright 2023 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/inrcot>
"""

from .constants import DEFAULT_POLL_INTERVAL, DEFAULT_COT_STALE, DEFAULT_COT_TYPE

from .functions import create_tasks, inreach_to_cot, split_feed, create_feeds

from .classes import Worker

__author__ = "Greg Albrecht <oss@undef.net>"
__copyright__ = "Copyright 2023 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
