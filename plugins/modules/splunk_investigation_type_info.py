#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: splunk_investigation_type_info
short_description: Gather information about Splunk Enterprise Security investigation types
description:
  - This module allows for querying information about Splunk Enterprise Security
    investigation types.
  - Use this module to retrieve investigation type configurations without making changes.
  - Query by C(name) to get a specific investigation type.
  - If C(name) is not specified, returns all investigation types.
version_added: "5.1.0"
options:
  name:
    description:
      - Name to filter investigation types.
      - Returns the investigation type with an exact name match.
      - If not specified, returns all investigation types.
    required: false
    type: str
  api_namespace:
    description:
      - The namespace portion of the Splunk API path.
      - Override this if your environment uses a different namespace.
    type: str
    default: servicesNS
  api_user:
    description:
      - The user portion of the Splunk API path.
      - Override this if your environment requires a different user context.
    type: str
    default: nobody
  api_app:
    description:
      - The app portion of the Splunk API path for the incident types endpoint.
      - Override this if your environment uses a different app name.
    type: str
    default: missioncontrol

author: Ron Gershburg (@rgershbu)
"""

EXAMPLES = """
- name: Query all investigation types
  splunk.es.splunk_investigation_type_info:
  register: all_types

- name: Query specific investigation type by name
  splunk.es.splunk_investigation_type_info:
    name: "Insider Threat"
  register: result

- name: Query investigation types with custom API path
  splunk.es.splunk_investigation_type_info:
    api_namespace: "{{ es_namespace | default('servicesNS') }}"
    api_user: "{{ es_user | default('nobody') }}"
    api_app: "{{ es_app | default('missioncontrol') }}"
  register: custom_types

- name: Get response plan IDs for an investigation type
  splunk.es.splunk_investigation_type_info:
    name: "Malware Incident"
  register: result
"""

RETURN = """
investigation_types:
  description: List of investigation types matching the query
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: The name of the investigation type
      type: str
    description:
      description: Description of the investigation type
      type: str
    response_plan_ids:
      description: List of response plan UUIDs associated with this investigation type
      type: list
      elements: str
  sample:
    - name: "Insider Threat"
      description: "Investigation type for insider threat incidents"
      response_plan_ids: []
    - name: "Malware Incident"
      description: "Investigation type for malware-related incidents"
      response_plan_ids:
        - "3415de6d-cdfb-4bdb-a21d-693cde38f1e8"
"""
