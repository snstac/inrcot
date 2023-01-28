Garmin inReach to Cursor on Target Gateway
******************************************

.. image:: https://raw.githubusercontent.com/ampledata/inrcot/main/docs/az-ccso-sar.jpg
   :alt: Screenshot of INRCOT being used on a Search & Rescue mission in Arizona.
   :target: https://raw.githubusercontent.com/ampledata/inrcot/main/docs/az-ccso-sar.jpg

* Pictured: Screenshot of INRCOT being used on a Search & Rescue mission in Arizona.

The inReach to Cursor on Target Gateway (INRCOT) transforms Garmin inReach
position messages into Cursor on Target (CoT) for display on TAK Products such as 
ATAK, WinTAK, iTAK, et al. Single or multi-device feeds are supported.

Other situational awareness products, including as RaptorX, TAKX & COPERS have been 
tested.

INRCOT requires a `Garmin inReach <https://discover.garmin.com/en-US/inreach/personal/>`_ 
device with service.

.. image:: https://raw.githubusercontent.com/ampledata/inrcot/main/docs/inrcot-conop.png
   :alt: Diagram of INRCOT's Concept of Operations (CONOP).
   :target: https://raw.githubusercontent.com/ampledata/inrcot/main/docs/inrcot-conop.png

* Pictured: Diagram of INRCOT's Concept of Operations (CONOP).


Support Development
===================

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
    :target: https://www.buymeacoffee.com/ampledata
    :alt: Support Development: Buy me a coffee!


Use Cases
=========

There are numerous applications for satellite based position location information, 
including:

1. Wildland fire unit tracking
2. Blue Force Tracking
3. Search & Rescue (SAR)
4. Partner Forces PLI
5. Asset Tracking
6. Data diode, CDS & cybersecurity considerations

See also Section 1114.d of the `Dingell Act <https://www.congress.gov/bill/116th-congress/senate-bill/47/text>`_::

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


Requirements
============

INRCOT uses the Garmin Explore "MapShare" feature.

1. Login to Garmin Explore: https://explore.garmin.com/
2. Browse to the "MY INFO" page: https://explore.garmin.com/Inbox
3. Click "Social".
4. Under MapShare > Enable MapShare click to enable 'MapShare: On'.
5. Click "Feeds" and note the "Raw KML Data" URL, we'll use this URL, write it down.

For more information on inReach KML Feeds see: https://support.garmin.com/en-US/?faq=tdlDCyo1fJ5UxjUbA9rMY8


Install
=======

INRCOT functionality is provided via a command-line tool named ``inrcot``. 
To install ``inrcot``:

Debian, Ubuntu, Raspbian, Raspberry OS::
    
    $ sudo apt update
    $ wget https://github.com/ampledata/pytak/releases/latest/download/python3-pytak_latest_all.deb
    $ sudo apt install -f ./python3-pytak_latest_all.deb
    $ wget https://github.com/ampledata/inrcot/releases/latest/download/python3-inrcot_latest_all.deb
    $ sudo apt install -f ./python3-inrcot_latest_all.deb

CentOS, et al::

    $ sudo python3 -m pip install inrcot

Install from source::
    
    $ git clone https://github.com/ampledata/inrcot.git
    $ cd inrcot/
    $ python3 setup.py install


Usage
=====

The ``inrcot`` program has two command-line arguments::

    $ inrcot -h
    usage: inrcot [-h] [-c CONFIG_FILE] [-p PREF_PACKAGE]

    optional arguments:
    -h, --help            show this help message and exit
    -c CONFIG_FILE, --CONFIG_FILE CONFIG_FILE
                            Optional configuration file. Default: config.ini
    -p PREF_PACKAGE, --PREF_PACKAGE PREF_PACKAGE
                            Optional connection preferences package zip file (aka data package).


Configuration
=============

Configuration parameters can be specified either via environment variables or in
a INI-stile configuration file. An example configuration file, click here for an 
example configuration file `example-config.ini <https://github.com/ampledata/inrcot/blob/main/example-config.ini>`_.

Global Config Parameters:

* **POLL_INTERVAL**: How many seconds between checking for new messages at the Spot API? Default: ``120`` (seconds).
* **COT_STALE**: How many seconds until CoT is stale? Default: ``600`` (seconds)
* **COT_TYPE**: CoT Type. Default: ``a-f-g-e-s``

For each feed (1 inReach = 1 feed, multiple feeds supported), these config params can be set:

* **FEED_URL**: URL to the MapShare KML.
* **COT_STALE**: How many seconds until CoT is stale? Default: ``600`` (seconds)
* **COT_TYPE**: CoT Type. Default: ``a-f-g-e-s``
* **COT_NAME**: CoT Callsign. Defaults to the MapShare KML Placemark name.
* **COT_ICON**: CoT User Icon. If set, will set the CoT ``usericon`` element, for use with custom TAK icon sets.
* **FEED_USERNAME**: MapShare username, for use with protected MapShare.
* **FEED_PASSWORD**: MapShare password, for use with protected MapShare.

TLS & other configuration parameters available via `PyTAK <https://github.com/ampledata/pytak#configuration-parameters>`_.


Example Configurations
======================

An example config::

    [inrcot]
    COT_URL = tcp://takserver.example.com:8088
    POLL_INTERVAL = 120

    [inrcot_feed_aaa]
    FEED_URL = https://share.garmin.com/Feed/Share/aaa

Multiple feeds can be added by creating multiple `inrcot_feed` sections::

    [inrcot]
    COT_URL = tcp://takserver.example.com:8088
    POLL_INTERVAL = 120

    [inrcot_feed_xxx]
    FEED_URL = https://share.garmin.com/Feed/Share/xxx

    [inrcot_feed_yyy]
    FEED_URL = https://share.garmin.com/Feed/Share/yyy

Individual feeds CoT output can be customized as well::

    [inrcot]
    COT_URL = tcp://takserver.example.com:8088
    POLL_INTERVAL = 120

    [inrcot_feed_zzz]
    FEED_URL = https://share.garmin.com/Feed/Share/zzz
    COT_TYPE = a-f-G-U-C
    COT_STALE = 600
    COT_NAME = Team Lead
    COT_ICON = my_package/team_lead.png

Protected feeds are also supported::

    [inrcot]
    COT_URL = tcp://takserver.example.com:8088
    POLL_INTERVAL = 120

    [inrcot_feed_ppp]
    FEED_URL = https://share.garmin.com/Feed/Share/ppp
    FEED_USERNAME = secretsquirrel
    FEED_PASSWORD = supersecret



Source
======
INRCOT Source can be found on Github: https://github.com/ampledata/inrcot


Author
======
INRCOT is written and maintained by Greg Albrecht W2GMD oss@undef.net

https://ampledata.org/


Copyright
=========
INRCOT is Copyright 2023 Greg Albrecht


License
=======
Copyright 2023 Greg Albrecht <oss@undef.net>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
