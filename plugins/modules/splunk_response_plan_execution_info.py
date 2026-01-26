#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: splunk_response_plan_execution_info
short_description: Gather information about applied response plans on an investigation
description:
  - This module retrieves information about response plans applied to a Splunk Enterprise Security investigation.
  - Returns the complete structure of applied response plans including phases and task statuses.
  - Use this module to query the current state of response plan execution without making changes.
version_added: "5.1.0"
options:
  investigation_ref_id:
    description:
      - The investigation UUID to query for applied response plans.
      - This is the unique identifier of the investigation (incident).
    type: str
    required: true
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
      - The app portion of the Splunk API path.
      - Override this if your environment uses a different app name.
    type: str
    default: missioncontrol

author: Ron Gershburg (@rgershbu)
"""

EXAMPLES = """
- name: Get applied response plans for an investigation
  splunk.es.splunk_response_plan_execution_info:
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
  register: result

- name: Display applied response plans
  debug:
    var: result.applied_response_plans

- name: Query with custom API path
  splunk.es.splunk_response_plan_execution_info:
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
    api_namespace: "{{ es_namespace | default('servicesNS') }}"
    api_user: "{{ es_user | default('nobody') }}"
    api_app: "{{ es_app | default('missioncontrol') }}"
  register: custom_result
"""

RETURN = """
applied_response_plans:
  description: List of response plans applied to the investigation
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique ID of the applied response plan instance
      type: str
    name:
      description: Name of the response plan
      type: str
    description:
      description: Description of the response plan
      type: str
    source_template_id:
      description: The ID of the response plan template this was created from
      type: str
    phases:
      description: List of phases in the applied response plan
      type: list
      elements: dict
      contains:
        id:
          description: The unique ID of the phase
          type: str
        name:
          description: Name of the phase
          type: str
        tasks:
          description: List of tasks in the phase
          type: list
          elements: dict
          contains:
            id:
              description: The unique ID of the task
              type: str
            name:
              description: Name of the task
              type: str
            description:
              description: Description of the task
              type: str
            status:
              description: >
                Current status of the task.
                Values are C(pending), C(started), or C(ended).
              type: str
            owner:
              description: >
                Owner/assignee of the task.
                Use C(admin) for the administrator user.
                Use C(unassigned) when no owner is assigned.
              type: str
            is_note_required:
              description: Whether a note is required when completing the task
              type: bool
  sample:
    - id: "b9e54dd3-d99c-4a17-bfde-17321d973511"
      name: "Incident Response Plan"
      description: "Standard incident response procedure"
      source_template_id: "77b3888b-a25e-4def-89fa-071fdcc10e47"
      phases:
        - id: "1ad365e7-ae1e-4023-99c1-eb58dd11b250"
          name: "Investigation Phase"
          tasks:
            - id: "3226b3dc-a31b-4987-b76c-3cdb32135f37"
              name: "Initial Triage"
              description: "Perform initial assessment"
              status: "started"
              owner: "admin"
              is_note_required: false
            - id: "2c73e6c5-35ec-454a-bba0-aa12a3297d56"
              name: "Gather Evidence"
              description: "Collect relevant logs"
              status: "pending"
              owner: "unassigned"
              is_note_required: false
changed:
  description: Always returns false as this is an info module
  returned: always
  type: bool
  sample: false
"""
