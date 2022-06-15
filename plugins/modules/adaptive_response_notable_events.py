#!/usr/bin/python
# -*- coding: utf-8 -*-
# https://github.com/ansible/ansible/issues/65816
# https://github.com/PyCQA/pylint/issues/214

# Copyright 2022 Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: adaptive_response_notable_events
short_description: Manage Splunk Enterprise Security Notable Event Adaptive Responses
description:
  - This module allows for creation, deletion, and modification of Splunk
    Enterprise Security Notable Event Adaptive Responses that are associated
    with a correlation search
  - Tested against Splunk Enterprise Server 8.2.3
version_added: "2.0.0"
options:
  config:
    description:
      - Configure file and directory monitoring on the system
    type: list
    elements: dict
    suboptions:
      name:
        description:
        - Name of notable event
        required: True
        type: str
      correlation_search_name:
        description:
          - Name of correlation search to associate this notable event adaptive response with
        required: true
        type: str
      description:
        description:
          - Description of the notable event, this will populate the description field for the web console
        type: str
      security_domain:
        description:
          - Splunk Security Domain
        type: str
        choices:
          - "access"
          - "endpoint"
          - "network"
          - "threat"
          - "identity"
          - "audit"
        default: "threat"
      severity:
        description:
          - Severity rating
        type: str
        choices:
          - "informational"
          - "low"
          - "medium"
          - "high"
          - "critical"
          - "unknown"
        default: "high"
      default_owner:
        description:
          - Default owner of the notable event, if unset it will default to Splunk System Defaults
        type: str
      default_status:
        description:
          - Default status of the notable event, if unset it will default to Splunk System Defaults
        type: str
        choices:
          - "unassigned"
          - "new"
          - "in progress"
          - "pending"
          - "resolved"
          - "closed"
      drilldown_name:
        description:
          - Name for drill down search, Supports variable substitution with fields from the matching event.
        type: str
      drilldown_search:
        description:
          - Drill down search, Supports variable substitution with fields from the matching event.
        type: str
      drilldown_earliest_offset:
        description:
          - Set the amount of time before the triggering event to search for related
            events. For example, 2h. Use '$info_min_time$' to set the drill-down time
            to match the earliest time of the search
        type: str
        default: '$info_min_time$'
      drilldown_latest_offset:
        description:
          - Set the amount of time after the triggering event to search for related
            events. For example, 1m. Use '$info_max_time$' to set the drill-down
            time to match the latest time of the search
        type: str
        default: '$info_max_time$'
      investigation_profiles:
        description:
          - Investigation profile to associate the notable event with.
        type: list
        elements: str
      next_steps:
        description:
          - List of adaptive responses that should be run next
          - Describe next steps and response actions that an analyst could take to address this threat.
        type: list
        elements: str
      recommended_actions:
        description:
          - List of adaptive responses that are recommended to be run next
          - Identifying Recommended Adaptive Responses will highlight those actions
            for the analyst when looking at the list of response actions available,
            making it easier to find them among the longer list of available actions.
        type: list
        elements: str
      extract_artifacts:
        description:
          - Assets and identities to be extracted
        type: dict
        suboptions:
          asset:
            description:
              - list of assets to extract, select any one or many of the available choices
              - defaults to all available choices
            type: list
            elements: str
            choices:
              - src
              - dest
              - dvc
              - orig_host
          file:
            description:
              - list of files to extract
            type: list
            elements: str
          identity:
            description:
              - list of identity fields to extract, select any one or many of the available choices
              - defaults to 'user' and 'src_user'
            type: list
            elements: str
            choices:
              - user
              - src_user
              - src_user_id
              - user_id
              - src_user_role
              - user_role
              - vendor_account
          url:
            description:
              - list of URLs to extract
            type: list
            elements: str
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
    - deleted
    - gathered
    default: merged

author: Pranav Bhatt (@pranav-bhatt)
"""

EXAMPLES = """
# _________________________________________________________________
# Using gathered

- name:
  splunk.es.data_inputs_monitors:
    config:
      - name: "/var/log"
      - name: "/var"
    state: gathered
#
# Output:
#
# "changed": false,
# "gathered": [
#     {
#         "blacklist": "//var/log/[a-z0-9]/gm",
#         "crc_salt": "<SOURCE>",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "host_regex": "/(test_host)/gm",
#         "host_segment": 3,
#         "index": "default",
#         "name": "/var/log",
#         "recursive": true,
#         "sourcetype": "test_source",
#         "whitelist": "//var/log/[0-9]/gm"
#     },
#     { } # there is no configuration associated with "/var"
# ]
#
# ------------------------------
# _________________________________________________________________
# Using merged
- name: Example adding data input monitor with splunk.es.data_input_monitor
  splunk.es.data_inputs_monitors:
    config:
      - name: "/var/log"
        blacklist: "//var/log/[a-z]/gm"
        check_index: True
        check_path: True
        crc_salt: <SOURCE>
        rename_source: "test"
        whitelist: "//var/log/[0-9]/gm"
    state: merged
#
# Output:
#
# "after": [
#     {
#         "blacklist": "//var/log/[a-z]/gm",
#         "crc_salt": "<SOURCE>",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "host_regex": "/(test_host)/gm",
#         "host_segment": 3,
#         "index": "default",
#         "name": "/var/log",
#         "recursive": true,
#         "sourcetype": "test_source",
#         "whitelist": "//var/log/[0-9]/gm"
#     }
# ],
# "before": [
#     {
#         "blacklist": "//var/log/[a-z0-9]/gm",
#         "crc_salt": "<SOURCE>",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "host_regex": "/(test_host)/gm",
#         "host_segment": 3,
#         "index": "default",
#         "name": "/var/log",
#         "recursive": true,
#         "sourcetype": "test_source",
#         "whitelist": "//var/log/[0-9]/gm"
#     }
# ],
# "changed": true
#
# ------------------------------
# _________________________________________________________________
# Using replaced

- name: Example adding data input monitor with splunk.es.data_input_monitor
  splunk.es.data_inputs_monitors:
    config:
      - name: "/var/log"
        blacklist: "//var/log/[a-z0-9]/gm"
        crc_salt: <SOURCE>
        index: default
    state: replaced
#
# Output:
#
# "after": [
#     {
#         "blacklist": "//var/log/[a-z0-9]/gm",
#         "crc_salt": "<SOURCE>",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "/var/log"
#     }
# ],
# "before": [
#     {
#         "blacklist": "//var/log/[a-z0-9]/gm",
#         "crc_salt": "<SOURCE>",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "host_regex": "/(test_host)/gm",
#         "host_segment": 3,
#         "index": "default",
#         "name": "/var/log",
#         "recursive": true,
#         "sourcetype": "test_source",
#         "whitelist": "//var/log/[0-9]/gm"
#     }
# ],
# "changed": true
#
# ------------------------------
# _________________________________________________________________
# Using deleted
- name: Example adding data input monitor with splunk.es.data_input_monitor
  splunk.es.data_inputs_monitors:
    config:
      - name: "/var/log"
    state: deleted
#
# Output:
#
# "after": [],
# "before": [
#     {
#         "blacklist": "//var/log/[a-z0-9]/gm",
#         "crc_salt": "<SOURCE>",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "/var/log"
#     }
# ],
# "changed": true
#
"""
