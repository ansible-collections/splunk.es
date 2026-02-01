#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: splunk_investigation_type
short_description: Manage Splunk Enterprise Security investigation types
description:
  - This module allows for creation and update of Splunk Enterprise Security
    investigation types.
  - Investigation type names are unique in Splunk ES, so C(name) is used as the identifier.
  - The module creates the investigation type if it does not exist, or updates it if it does.
  - Response plans can be associated with investigation types via C(response_plan_ids).
  - B(Note:) Investigation types cannot be deleted via the Splunk API, so this module
    only supports create and update operations.
  - B(IMPORTANT - Declarative Approach:) The C(response_plan_ids) parameter is declarative.
    Whatever response plan IDs you define will be exactly what is associated with the
    investigation type after the module runs. Any existing associations NOT included
    in your playbook will be REMOVED.
version_added: "5.1.0"
options:
  name:
    description:
      - The name of the investigation type.
      - This is the unique identifier and is always required.
      - The name cannot be changed after creation.
    type: str
    required: true
  description:
    description:
      - The description of the investigation type.
    type: str
  response_plan_ids:
    description:
      - List of response plan tempalte UUIDs to associate with this investigation type.
      - Use the C(splunk_response_plan_info) module to get response plan template IDs.
      - If not specified or empty, no response plans will be associated.
      - B(Note:) This is declarative - only the IDs listed here will be associated.
        Any existing associations not in this list will be removed.
    type: list
    elements: str
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
# Create a new investigation type
- name: Create investigation type
  splunk.es.splunk_investigation_type:
    name: "Insider Threat"
    description: "Investigation type for insider threat incidents"

# Create investigation type with response plan associations
- name: Create investigation type with response plans
  splunk.es.splunk_investigation_type:
    name: "Malware Incident"
    description: "Investigation type for malware-related incidents"
    response_plan_ids:
      - "3415de6d-cdfb-4bdb-a21d-693cde38f1e8"
      - "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# Update investigation type description
- name: Update investigation type description
  splunk.es.splunk_investigation_type:
    name: "Insider Threat"
    description: "Updated description for insider threat investigations"

# Update response plan associations (replaces existing associations)
- name: Update investigation type response plans
  splunk.es.splunk_investigation_type:
    name: "Malware Incident"
    description: "Investigation type for malware-related incidents"
    response_plan_ids:
      - "new-uuid-1234-5678-abcd-ef1234567890"

# Remove all response plan associations
- name: Remove all response plans from investigation type
  splunk.es.splunk_investigation_type:
    name: "Malware Incident"
    description: "Investigation type for malware-related incidents"
    response_plan_ids: []

# Create investigation type with custom API path
- name: Create investigation type with custom API path
  splunk.es.splunk_investigation_type:
    name: "Custom Investigation Type"
    description: "Investigation type with custom API configuration"
    api_namespace: "{{ es_namespace | default('servicesNS') }}"
    api_user: "{{ es_user | default('nobody') }}"
    api_app: "{{ es_app | default('missioncontrol') }}"
"""

RETURN = """
investigation_type:
  description: The investigation type result containing before/after states.
  returned: always
  type: dict
  contains:
    before:
      description: The investigation type state before module execution (null if creating).
      type: dict
      returned: when investigation type existed
    after:
      description: The investigation type state after module execution.
      type: dict
      returned: always
  sample:
    before: null
    after:
      name: "Malware Incident"
      description: "Investigation type for malware-related incidents"
      response_plan_ids:
        - "3415de6d-cdfb-4bdb-a21d-693cde38f1e8"
changed:
  description: Whether any changes were made.
  returned: always
  type: bool
  sample: true
msg:
  description: Message describing the result.
  returned: always
  type: str
  sample: "Investigation type created successfully"
"""
