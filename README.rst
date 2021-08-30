inrcot - Garmin inReach to Cursor-on-Target Gateway.
****************************************************

IF YOU HAVE AN URGENT OPERATIONAL NEED: Email ops@undef.net or call/sms +1-415-598-8226

.. image:: docs/ScreenShot2021-01-08at4.18.37PM.png
   :alt: Screenshot of inReach CoT PLI Point in ATAK
   :target: docs/ScreenShot2021-01-08at4.18.37PM.png

The ``inrcot`` inReach to Cursor-on-Target Gateway transforms Garmin inReach
position messages into Cursor on Target (CoT) Position Location Information
(PLI) Points for display on Situational Awareness (SA) applications such as the
Android Team Awareness Kit (ATAK), WinTAK, RaptorX, COPERS, et al.

Possible use-cases include tracking Search & Rescue (SAR) operators, or
integrating Partner Forces location data into existing SA infrastructure
without exposing private network elements.

``inrcot`` can be run as a foreground command line application, but should be
run as a service with tools like systemd or `supervisor <http://supervisord.org/>`_

Usage of this program requires a `Garmin iNReach <https://discover.garmin.com/en-US/inreach/personal/>`_ device with service.

Wildland Firefighting
=====================
``inrcot`` may also be of use in wildland firefighting, see Section 1114.d of the `Dingell Act <https://www.congress.gov/bill/116th-congress/senate-bill/47/text>`_::

    Location Systems for Wildland Firefighters.--
    (1) In general.--Not later than 2 years after the date of
        enactment of this Act, subject to the availability of
        appropriations, the Secretaries, in coordination with State
        wildland firefighting agencies, shall jointly develop and
        operate a tracking system (referred to in this subsection as the
        ``system'') to remotely locate the positions of fire resources
        for use by wildland firefighters, including, at a minimum, any
        fire resources assigned to Federal type 1 wildland fire incident
        management teams.


Installation
============

To install from this source tree::

    $ git checkout https://github.com/ampledata/inrcot.git
    $ cd inrcot/
    $ python setup.py install

To install from PyPI::

    $ pip install inrcot


Setup
=====

``inrcot`` uses the Garmin inReach **KML Feed** feature to retrieve Spot location
messages from the Spot API.

To enable the **XML Feed** feature:

1. Login to your Spot account at: https://login.findmespot.com/spot-main-web/auth/login.html
2. In the navigation bar, click **XML Feed**, then **Create XML Feed**.
3. Enter any value for **XML Feed Name**.
4. *[Optional]* If you select **Make XML page private**, chose and record a password.
5. Click **Create**, record the **XML Feed ID**.

Usage
=====

The `inrcot` program has one command-line argument::

    $ inrcot -h
    usage: inrcot [-h] [-c CONFIG_FILE]

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --CONFIG_FILE CONFIG_FILE

You must create a configuration file, see `example-config.ini` in the source
respository.

An example config::

    [inrcot]
    COT_URL = tcp:takserver.example.com:8088
    POLL_INTERVAL = 120

    [inrcot_feed_aaa]
    FEED_URL = https://share.garmin.com/Feed/Share/aaa

Multiple feeds can be added by creating multiple `inrcot_feed` sections::

    [inrcot]
    COT_URL = tcp:takserver.example.com:8088
    POLL_INTERVAL = 120

    [inrcot_feed_xxx]
    FEED_URL = https://share.garmin.com/Feed/Share/xxx

    [inrcot_feed_yyy]
    FEED_URL = https://share.garmin.com/Feed/Share/yyy

Individual feeds CoT output can be customized as well::

    [inrcot]
    COT_URL = tcp:takserver.example.com:8088
    POLL_INTERVAL = 120

    [inrcot_feed_zzz]
    FEED_URL = https://share.garmin.com/Feed/Share/zzz
    COT_TYPE = a-f-G-U-C
    COT_STALE = 600
    COT_NAME = Team Lead
    COT_ICON = my_package/team_lead.png


Source
======
Github: https://github.com/ampledata/inrcot

Author
======
Greg Albrecht W2GMD oss@undef.net

https://ampledata.org/

Copyright
=========
Copyright 2021 Greg Albrecht

License
=======
Apache License, Version 2.0. See LICENSE for details.
