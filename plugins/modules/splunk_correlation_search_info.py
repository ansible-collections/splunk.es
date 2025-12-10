#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2022 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = """
---
module: splunk_correlation_search_info
short_description: Gather information about Splunk Enterprise Security Correlation Searches
description:
  - This module allows for querying information about Splunk Enterprise Security Correlation Searches.
  - Use this module to retrieve correlation search configurations without making changes.
  - This module uses the httpapi connection plugin and does not require local Splunk SDK.
version_added: "3.0.0"
options:
  name:
    description:
      - Name of correlation search to query.
      - If not specified, returns all correlation searches.
    required: false
    type: str

author: Ansible Security Automation Team (@ansible-security)
"""

EXAMPLES = """
- name: Query specific correlation search by name
  splunk.es.splunk_correlation_search_info:
    name: "Brute Force Access Behavior Detected"
  register: result

- name: Display the correlation search info
  debug:
    var: result.correlation_searches

- name: Query all correlation searches
  splunk.es.splunk_correlation_search_info:
  register: all_searches

- name: Display all correlation searches
  debug:
    var: all_searches.correlation_searches

- name: Find searches containing specific keyword
  splunk.es.splunk_correlation_search_info:
  register: all_searches

- set_fact:
    filtered_searches: "{{ all_searches.correlation_searches |
                          selectattr('name', 'search', 'Brute Force') | list }}"
"""

RETURN = """
correlation_searches:
  description: Information about correlation search(es)
  returned: always
  type: dict
  contains:
    entry:
      description: List of correlation search entries
      type: list
      elements: dict
  sample:
    entry:
      - name: "Brute Force Access Behavior Detected"
        content:
          description: "Detects brute force behavior"
          search: "| from datamodel:Authentication"
          disabled: 0
"""
