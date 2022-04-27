#!/usr/bin/python
# -*- coding: utf-8 -*-
# https://github.com/ansible/ansible/issues/65816
# https://github.com/PyCQA/pylint/issues/214

# (c) 2022, Pranav Bhatt (adpranavb2000@gmail.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: data_inputs_monitors
short_description: Manage Splunk Data Inputs of type Monitor
description:
  - This module allows for addition or deletion of File and Directory Monitor Data Inputs in Splunk.
  - Tested against Splunk Enterprise Server 8.2.3
version_added: "2.0.0"
options:
  config:
    description:
      - Configure file and directory monitoring on the system
    type: list
    subelement: dict
    suboptions:
      name:
        description:
        - The file or directory path to monitor on the system.
        required: True
        type: str
      blacklist:
        description:
          - Specify a regular expression for a file path. The file path that matches this regular expression is not indexed.
        required: False
        type: str
      check_index:
        description:
          - If set to C(True), the index value is checked to ensure that it is the name of a valid index.
          - This parameter is not returned back by Splunk while obtaining object information.
            It is therefore left out while performing idempotency checks
        required: False
        type: bool
        default: False
      check_path:
        description:
          - If set to C(True), the name value is checked to ensure that it exists.
          - This parameter is not returned back by Splunk while obtaining object information.
            It is therefore left out while performing idempotency checks
        required: False
        type: bool
      crc_salt:
        description:
          - A string that modifies the file tracking identity for files in this input.
            The magic value <SOURCE> invokes special behavior (see admin documentation).
        required: False
        type: str
      disabled:
        description:
          - Indicates if input monitoring is disabled.
        required: False
        default: False
        type: bool
      follow_tail:
        description:
          - If set to C(True), files that are seen for the first time is read from the end.
        required: False
        type: bool
        default: False
      host:
        description:
          - The value to populate in the host field for events from this data input.
        required: False
        type: str
      host_regex:
        description:
          - Specify a regular expression for a file path. If the path for a file
            matches this regular expression, the captured value is used to populate
            the host field for events from this data input. The regular expression
            must have one capture group.
        required: False
        type: str
      host_segment:
        description:
          - Use the specified slash-separate segment of the filepath as the host field value.
        required: False
        type: int
      ignore_older_than:
        description:
          - Specify a time value. If the modification time of a file being monitored
            falls outside of this rolling time window, the file is no longer being monitored.
          - This parameter is not returned back by Splunk while obtaining object information.
            It is therefore left out while performing idempotency checks
        required: False
        type: str
      index:
        description:
          - Which index events from this input should be stored in. Defaults to default.
        required: False
        type: str
      recursive:
        description:
          - Setting this to False prevents monitoring of any subdirectories encountered within this data input.
        required: False
        type: bool
        default: False
      rename_source:
        description:
          - The value to populate in the source field for events from this data input.
            The same source should not be used for multiple data inputs.
          - This parameter is not returned back by Splunk while obtaining object information.
            It is therefore left out while performing idempotency checks
        required: False
        type: str
      sourcetype:
        description:
          - The value to populate in the sourcetype field for incoming events.
        required: False
        type: str
      time_before_close:
        description:
          - When Splunk software reaches the end of a file that is being read, the
            file is kept open for a minimum of the number of seconds specified in
            this value. After this period has elapsed, the file is checked again for
            more data.
          - This parameter is not returned back by Splunk while obtaining object information.
            It is therefore left out while performing idempotency checks
        required: False
        type: int
      whitelist:
        description:
          - Specify a regular expression for a file path. Only file paths that match this regular expression are indexed.
        required: False
        type: str
    
  running_config:
    description:
    - The module, by default, will connect to the remote device and retrieve the current
      running-config to use as a base for comparing against the contents of source.
      There are times when it is not desirable to have the task get the current running-config
      for every task in a playbook.  The I(running_config) argument allows the implementer
      to pass in the configuration to use as the base config for comparison. This
      value of this option should be the output received from device by executing
      command.
    type: str
  state:
    description:
    - The state the configuration should be left in
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    - gathered
    - rendered
    - parsed
    default: merged

author: Pranav Bhatt (@pranav-bhatt)
"""

EXAMPLES = """
- name: Example adding data input monitor with splunk.es.data_input_monitor
  splunk.es.data_input_monitor:
    name: "/var/log"
    blacklist: "/\/var\/log\/[a-z]/gm"
    check_index: True
    check_path: True
    crc_salt: <SOURCE>
    host_regex: "/(test_host)/gm"
    ignore_older_than: 7d
    index: default
    sourcetype: test_source
    time_before_close: 5
    state: "present"
    recursive: True
    whitelist: "/\/var\/log\/[0-9]/gm"

- name: Example adding data input monitor with splunk.es.data_input_monitor
  splunk.es.data_input_monitors:
    config:
      - name: "/var/log"
        blacklist: "/\/var\/log\/[a-z0-9]/gm"
        check_index: True
        check_path: True
        crc_salt: <SOURCE>
        host_regex: "/(test_host)/gm"
        host_segment: 3
        ignore_older_than: 7d
        index: default
        sourcetype: test_source
        time_before_close: 5
        recursive: True
        rename_source: "test"
        whitelist: "/\/var\/log\/[0-9]/gm"
    state: replaced
"""
